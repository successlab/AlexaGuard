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

package org.openqa.selenium.grid.node.local;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import org.junit.Before;
import org.junit.Test;
import org.openqa.selenium.Capabilities;
import org.openqa.selenium.ImmutableCapabilities;
import org.openqa.selenium.NoSuchSessionException;
import org.openqa.selenium.events.EventBus;
import org.openqa.selenium.events.local.GuavaEventBus;
import org.openqa.selenium.grid.data.CreateSessionRequest;
import org.openqa.selenium.grid.data.CreateSessionResponse;
import org.openqa.selenium.grid.data.NodeStatus;
import org.openqa.selenium.grid.data.Session;
import org.openqa.selenium.grid.node.Node;
import org.openqa.selenium.grid.security.Secret;
import org.openqa.selenium.grid.testing.TestSessionFactory;
import org.openqa.selenium.remote.HttpSessionId;
import org.openqa.selenium.remote.SessionId;
import org.openqa.selenium.remote.http.HttpHandler;
import org.openqa.selenium.remote.http.HttpRequest;
import org.openqa.selenium.remote.http.HttpResponse;
import org.openqa.selenium.remote.tracing.DefaultTestTracer;
import org.openqa.selenium.remote.tracing.Tracer;

import java.net.URI;
import java.net.URISyntaxException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

import static java.util.concurrent.TimeUnit.SECONDS;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatExceptionOfType;
import static org.openqa.selenium.remote.Dialect.W3C;
import static org.openqa.selenium.remote.http.HttpMethod.GET;

public class LocalNodeTest {

  private LocalNode node;
  private Session session;
  private Secret registrationSecret;

  @Before
  public void setUp() throws URISyntaxException {
    Tracer tracer = DefaultTestTracer.createTracer();
    EventBus bus = new GuavaEventBus();
    URI uri = new URI("http://localhost:1234");
    Capabilities stereotype = new ImmutableCapabilities("cheese", "brie");
    registrationSecret = new Secret("red leicester");
    node = LocalNode.builder(tracer, bus, uri, uri, registrationSecret)
        .add(stereotype, new TestSessionFactory((id, caps) -> new Session(id, uri, stereotype, caps, Instant.now())))
        .build();

    CreateSessionResponse sessionResponse = node.newSession(
        new CreateSessionRequest(
            ImmutableSet.of(W3C),
            stereotype,
            ImmutableMap.of()))
        .orElseThrow(() -> new AssertionError("Unable to create session"));
    session = sessionResponse.getSession();
  }

  @Test
  public void shouldThrowIfSessionIsNotPresent() {
    assertThatExceptionOfType(NoSuchSessionException.class)
        .isThrownBy(() -> node.getSession(new SessionId("12345")));
  }

  @Test
  public void canRetrieveActiveSessionById() {
    assertThat(node.getSession(session.getId())).isEqualTo(session);
  }

  @Test
  public void isOwnerOfAnActiveSession() {
    assertThat(node.isSessionOwner(session.getId())).isTrue();
  }

  @Test
  public void canStopASession() {
    node.stop(session.getId());
    assertThatExceptionOfType(NoSuchSessionException.class)
        .isThrownBy(() -> node.getSession(session.getId()));
  }

  @Test
  public void isNotOwnerOfAStoppedSession() {
    node.stop(session.getId());
    assertThat(node.isSessionOwner(session.getId())).isFalse();
  }

  @Test
  public void cannotAcceptNewSessionsWhileDraining() {
    node.drain();
    assertThat(node.isDraining()).isTrue();
    node.stop(session.getId()); //stop the default session

    Capabilities stereotype = new ImmutableCapabilities("cheese", "brie");
    Optional<CreateSessionResponse> sessionResponse = node.newSession(
        new CreateSessionRequest(
            ImmutableSet.of(W3C),
            stereotype,
            ImmutableMap.of()));
    assertThat(sessionResponse).isEmpty();
  }

  @Test
  public void canReturnStatusInfo() {
    NodeStatus status = node.getStatus();
    assertThat(status.getSlots().stream()
      .filter(slot -> slot.getSession().isPresent())
      .map(slot -> slot.getSession().get())
      .filter(s -> s.getId().equals(session.getId()))).isNotEmpty();

    node.stop(session.getId());
    status = node.getStatus();
    assertThat(status.getSlots().stream()
      .filter(slot -> slot.getSession().isPresent())
      .map(slot -> slot.getSession().get())
      .filter(s -> s.getId().equals(session.getId()))).isEmpty();
  }

  @Test
  public void nodeStatusInfoIsImmutable() {
    NodeStatus status = node.getStatus();
    assertThat(status.getSlots().stream()
      .filter(slot -> slot.getSession().isPresent())
      .map(slot -> slot.getSession().get())
      .filter(s -> s.getId().equals(session.getId()))).isNotEmpty();

    node.stop(session.getId());
    assertThat(status.getSlots().stream()
      .filter(slot -> slot.getSession().isPresent())
      .map(slot -> slot.getSession().get())
      .filter(s -> s.getId().equals(session.getId()))).isNotEmpty();
  }

  @Test
  public void shouldBeAbleToCreateSessionsConcurrently() throws Exception {
    Tracer tracer = DefaultTestTracer.createTracer();
    EventBus bus = new GuavaEventBus();
    URI uri = new URI("http://localhost:1234");
    Capabilities caps = new ImmutableCapabilities("browserName", "cheese");

    class VerifyingHandler extends Session implements HttpHandler {
      private VerifyingHandler(SessionId id, Capabilities capabilities) {
        super(id, uri, new ImmutableCapabilities(), capabilities, Instant.now());
      }

      @Override
      public HttpResponse execute(HttpRequest req) {
        Optional<SessionId> id = HttpSessionId.getSessionId(req.getUri()).map(SessionId::new);
        assertThat(id).isEqualTo(Optional.of(getId()));
        return new HttpResponse();
      }
    }

    Node node = LocalNode.builder(tracer, bus, uri, uri, registrationSecret)
      .add(caps, new TestSessionFactory(VerifyingHandler::new))
      .add(caps, new TestSessionFactory(VerifyingHandler::new))
      .add(caps, new TestSessionFactory(VerifyingHandler::new))
      .build();

    List<Callable<SessionId>> callables = new ArrayList<>();
    for (int i = 0; i < 3; i++) {
      callables.add(() -> {
        CreateSessionResponse res = node.newSession(
          new CreateSessionRequest(
            ImmutableSet.of(W3C),
            caps,
            ImmutableMap.of()))
          .orElseThrow(() -> new AssertionError("Unable to create session"));
        assertThat(res.getSession().getCapabilities().getBrowserName()).isEqualTo("cheese");
        return res.getSession().getId();
      });
    }

    List<Future<SessionId>> futures = Executors.newFixedThreadPool(3).invokeAll(callables);

    for (Future<SessionId> future : futures) {
      SessionId id = future.get(2, SECONDS);

      // Now send a random command.
      HttpResponse res = node.execute(new HttpRequest(GET, String.format("/session/%s/url", id)));
      assertThat(res.isSuccessful()).isTrue();
    }
  }
}
