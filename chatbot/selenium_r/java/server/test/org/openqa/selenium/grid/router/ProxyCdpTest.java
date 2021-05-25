// Licensed to the Software Freedom Conservancy (SFC) under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  The SFC licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.

package org.openqa.selenium.grid.router;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.openqa.selenium.ImmutableCapabilities;
import org.openqa.selenium.events.EventBus;
import org.openqa.selenium.events.local.GuavaEventBus;
import org.openqa.selenium.grid.config.Config;
import org.openqa.selenium.grid.config.MapConfig;
import org.openqa.selenium.grid.data.Session;
import org.openqa.selenium.grid.server.BaseServerOptions;
import org.openqa.selenium.grid.server.Server;
import org.openqa.selenium.grid.sessionmap.SessionMap;
import org.openqa.selenium.grid.sessionmap.local.LocalSessionMap;
import org.openqa.selenium.netty.server.NettyServer;
import org.openqa.selenium.remote.SessionId;
import org.openqa.selenium.remote.http.HttpClient;
import org.openqa.selenium.remote.http.HttpHandler;
import org.openqa.selenium.remote.http.HttpRequest;
import org.openqa.selenium.remote.http.HttpResponse;
import org.openqa.selenium.remote.http.TextMessage;
import org.openqa.selenium.remote.http.WebSocket;
import org.openqa.selenium.remote.tracing.DefaultTestTracer;
import org.openqa.selenium.remote.tracing.Tracer;

import java.net.URISyntaxException;
import java.time.Instant;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicReference;

import static java.util.concurrent.TimeUnit.SECONDS;
import static org.assertj.core.api.Assertions.assertThat;
import static org.openqa.selenium.remote.http.HttpMethod.GET;

import com.google.common.collect.ImmutableMap;

public class ProxyCdpTest {

  private final HttpHandler nullHandler = req -> new HttpResponse();
  private final Config emptyConfig = new MapConfig(Map.of());
  private Server<?> proxyServer;
  private SessionMap sessions;

  @Before
  public void setUp() {
    Tracer tracer = DefaultTestTracer.createTracer();
    EventBus events = new GuavaEventBus();

    sessions = new LocalSessionMap(tracer, events);

    // Set up the proxy we'll be using
    HttpClient.Factory clientFactory = HttpClient.Factory.createDefault();

    ProxyCdpIntoGrid proxy = new ProxyCdpIntoGrid(clientFactory, sessions);
    proxyServer = new NettyServer(new BaseServerOptions(emptyConfig), nullHandler, proxy).start();
  }

  @After
  public void tearDown() {
    proxyServer.stop();
  }

  @Test
  public void shouldForwardTextMessageToServer() throws URISyntaxException, InterruptedException {
    HttpClient.Factory clientFactory = HttpClient.Factory.createDefault();

    // Create a backend server which will capture any incoming text message
    AtomicReference<String> text = new AtomicReference<>();
    CountDownLatch latch = new CountDownLatch(1);
    Server<?> backend = createBackendServer(latch, text, "", emptyConfig);

    // Push a session that resolves to the backend server into the session map
    SessionId id = new SessionId(UUID.randomUUID());
    sessions.add(new Session(id, backend.getUrl().toURI(), new ImmutableCapabilities(), new ImmutableCapabilities(), Instant.now()));

    // Now! Send a message. We expect it to eventually show up in the backend
    try (WebSocket socket = clientFactory.createClient(proxyServer.getUrl())
      .openSocket(new HttpRequest(GET, String.format("/session/%s/cdp", id)), new WebSocket.Listener(){})) {

      socket.sendText("Cheese!");

      assertThat(latch.await(5, SECONDS)).isTrue();
      assertThat(text.get()).isEqualTo("Cheese!");
    }
  }

  @Test
  public void shouldForwardTextMessageFromServerToLocalEnd() throws URISyntaxException, InterruptedException {
    HttpClient.Factory clientFactory = HttpClient.Factory.createDefault();

    Server<?> backend = createBackendServer(new CountDownLatch(1), new AtomicReference<>(), "Asiago", emptyConfig);

    // Push a session that resolves to the backend server into the session map
    SessionId id = new SessionId(UUID.randomUUID());
    sessions.add(new Session(id, backend.getUrl().toURI(), new ImmutableCapabilities(), new ImmutableCapabilities(), Instant.now()));

    // Now! Send a message. We expect it to eventually show up in the backend
    CountDownLatch latch = new CountDownLatch(1);
    AtomicReference<String> text = new AtomicReference<>();
    try(WebSocket socket = clientFactory.createClient(proxyServer.getUrl())
      .openSocket(new HttpRequest(GET, String.format("/session/%s/cdp", id)), new WebSocket.Listener() {
        @Override
        public void onText(CharSequence data) {
          text.set(data.toString());
          latch.countDown();
        }
      })) {

      socket.sendText("Cheese!");

      assertThat(latch.await(5, SECONDS)).isTrue();
      assertThat(text.get()).isEqualTo("Asiago");
    }
  }

  @Test
  public void shouldBeAbleToSendMessagesOverSecureWebSocket()
      throws URISyntaxException, InterruptedException {

    Config secureConfig = new MapConfig(ImmutableMap.of(
      "server", ImmutableMap.of(
        "https-self-signed", true)));

    HttpClient.Factory clientFactory = HttpClient.Factory.createDefault();
    ProxyCdpIntoGrid proxy = new ProxyCdpIntoGrid(clientFactory, sessions);

    Server<?> backend = createBackendServer(new CountDownLatch(1), new AtomicReference<>(), "Cheddar", emptyConfig);

    Server<?> secureProxyServer = new NettyServer(new BaseServerOptions(secureConfig), nullHandler, proxy);

    secureProxyServer.start();
    // Push a session that resolves to the backend server into the session map
    SessionId id = new SessionId(UUID.randomUUID());

    sessions.add(new Session(id, backend.getUrl().toURI(), new ImmutableCapabilities(), new ImmutableCapabilities(), Instant.now()));

    CountDownLatch latch = new CountDownLatch(1);
    AtomicReference<String> text = new AtomicReference<>();
    try (WebSocket socket = clientFactory.createClient(secureProxyServer.getUrl())
      .openSocket(new HttpRequest(GET, String.format("/session/%s/cdp", id)), new WebSocket.Listener() {
        @Override
        public void onText(CharSequence data) {
          text.set(data.toString());
          latch.countDown();
        }
      })) {
      socket.sendText("Cheese!");

      assertThat(latch.await(5, SECONDS)).isTrue();
      assertThat(text.get()).isEqualTo("Cheddar");
    }

    secureProxyServer.stop();
  }

  private Server<?> createBackendServer(CountDownLatch latch, AtomicReference<String> incomingRef, String response, Config config) {
    return new NettyServer(
      new BaseServerOptions(config),
      nullHandler,
      (uri, sink) -> Optional.of(msg -> {
        if (msg instanceof TextMessage) {
          incomingRef.set(((TextMessage) msg).text());
          sink.accept(new TextMessage(response));
          latch.countDown();
        }
      }))
      .start();
  }
}
