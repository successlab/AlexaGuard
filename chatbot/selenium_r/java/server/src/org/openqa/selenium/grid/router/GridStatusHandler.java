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

import com.google.common.collect.ImmutableMap;
import org.openqa.selenium.grid.data.DistributorStatus;
import org.openqa.selenium.grid.distributor.Distributor;
import org.openqa.selenium.internal.Require;
import org.openqa.selenium.json.Json;
import org.openqa.selenium.remote.http.HttpClient;
import org.openqa.selenium.remote.http.HttpHandler;
import org.openqa.selenium.remote.http.HttpRequest;
import org.openqa.selenium.remote.http.HttpResponse;
import org.openqa.selenium.remote.tracing.AttributeKey;
import org.openqa.selenium.remote.tracing.EventAttribute;
import org.openqa.selenium.remote.tracing.EventAttributeValue;
import org.openqa.selenium.remote.tracing.HttpTracing;
import org.openqa.selenium.remote.tracing.Span;
import org.openqa.selenium.remote.tracing.Status;
import org.openqa.selenium.remote.tracing.Tracer;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeoutException;

import static java.util.concurrent.TimeUnit.MILLISECONDS;
import static java.util.concurrent.TimeUnit.SECONDS;
import static java.util.stream.Collectors.toList;
import static org.openqa.selenium.json.Json.MAP_TYPE;
import static org.openqa.selenium.remote.http.Contents.asJson;
import static org.openqa.selenium.remote.http.Contents.string;
import static org.openqa.selenium.remote.http.HttpMethod.GET;
import static org.openqa.selenium.remote.tracing.HttpTracing.newSpanAsChildOf;
import static org.openqa.selenium.remote.tracing.Tags.EXCEPTION;
import static org.openqa.selenium.remote.tracing.Tags.HTTP_RESPONSE;
import static org.openqa.selenium.remote.tracing.Tags.HTTP_RESPONSE_EVENT;

class GridStatusHandler implements HttpHandler {

  private static final ScheduledExecutorService
      SCHEDULED_SERVICE =
      Executors.newScheduledThreadPool(
          1,
          r -> {
            Thread thread = new Thread(r, "Scheduled grid status executor");
            thread.setDaemon(true);
            return thread;
          });


  private static final ExecutorService EXECUTOR_SERVICE = Executors.newCachedThreadPool(
      r -> {
        Thread thread = new Thread(r, "Grid status executor");
        thread.setDaemon(true);
        return thread;
      });


  private final Json json;
  private final Tracer tracer;
  private final HttpClient.Factory clientFactory;
  private final Distributor distributor;

  GridStatusHandler(Json json, Tracer tracer, HttpClient.Factory clientFactory, Distributor distributor) {
    this.json = Require.nonNull("JSON encoder", json);
    this.tracer = Require.nonNull("Tracer", tracer);
    this.clientFactory = Require.nonNull("HTTP client factory", clientFactory);
    this.distributor = Require.nonNull("Distributor", distributor);
  }

  @Override
  public HttpResponse execute(HttpRequest req) {
    long start = System.currentTimeMillis();

    try (Span span = newSpanAsChildOf(tracer, req, "router.status")) {
      Map<String, EventAttributeValue> attributeMap = new HashMap<>();
      attributeMap.put(AttributeKey.LOGGER_CLASS.getKey(),
                       EventAttribute.setValue(getClass().getName()));
      DistributorStatus status;
      try {
        status = EXECUTOR_SERVICE.submit(span.wrap(distributor::getStatus)).get(2, SECONDS);
      } catch (ExecutionException | TimeoutException e) {
        span.setAttribute("error", true);
        span.setStatus(Status.CANCELLED);
        EXCEPTION.accept(attributeMap, e);
        attributeMap.put(AttributeKey.EXCEPTION_MESSAGE.getKey(),
                         EventAttribute.setValue("Unable to get distributor status due to execution error or timeout: " + e.getMessage()));
        span.addEvent(AttributeKey.EXCEPTION_EVENT.getKey(), attributeMap);

        return new HttpResponse().setContent(asJson(
          ImmutableMap.of("value", ImmutableMap.of(
            "ready", false,
            "message", "Unable to read distributor status."))));
      } catch (InterruptedException e) {
        span.setAttribute("error", true);
        span.setStatus(Status.ABORTED);
        EXCEPTION.accept(attributeMap, e);
        attributeMap.put(AttributeKey.EXCEPTION_MESSAGE.getKey(),
                         EventAttribute.setValue("Interruption while getting distributor status: " + e.getMessage()));

        Thread.currentThread().interrupt();
        return new HttpResponse().setContent(asJson(
          ImmutableMap.of("value", ImmutableMap.of(
            "ready", false,
            "message", "Reading distributor status was interrupted."))));
      }

      boolean ready = status.hasCapacity();

      long remaining = System.currentTimeMillis() + 2000 - start;
      List<Future<Map<String, Object>>> nodeResults = status.getNodes().stream()
        .map(node -> {
          ImmutableMap<String, Object> defaultResponse = ImmutableMap.of(
            "id", node.getId(),
            "uri", node.getUri(),
            "maxSessions", node.getMaxSessionCount(),
            "slots", node.getSlots(),
            "warning", "Unable to read data from node.");

          CompletableFuture<Map<String, Object>> toReturn = new CompletableFuture<>();

          Future<?> future = EXECUTOR_SERVICE.submit(
            () -> {
              try {
                HttpClient client = clientFactory.createClient(node.getUri().toURL());
                HttpRequest nodeStatusReq = new HttpRequest(GET, "/se/grid/node/status");
                HttpTracing.inject(tracer, span, nodeStatusReq);
                HttpResponse res = client.execute(nodeStatusReq);

                toReturn.complete(res.getStatus() == 200
                                  ? json.toType(string(res), MAP_TYPE)
                                  : defaultResponse);
              } catch (IOException e) {
                toReturn.complete(defaultResponse);
              }
            });

          SCHEDULED_SERVICE.schedule(
            () -> {
              if (!toReturn.isDone()) {
                toReturn.complete(defaultResponse);
                future.cancel(true);
              }
            },
            remaining,
            MILLISECONDS);

          return toReturn;
        })
        .collect(toList());

      ImmutableMap.Builder<String, Object> value = ImmutableMap.builder();
      value.put("ready", ready);
      value.put("message", ready ? "Selenium Grid ready." : "Selenium Grid not ready.");

      value.put("nodes", nodeResults.stream()
        .map(summary -> {
            try {
              return summary.get();
            } catch (ExecutionException e) {
              span.setAttribute("error", true);
              span.setStatus(Status.NOT_FOUND);
              EXCEPTION.accept(attributeMap, e);
              attributeMap.put(AttributeKey.EXCEPTION_MESSAGE.getKey(),
                               EventAttribute.setValue("Unable to get Node information: " + e.getMessage()));
              span.addEvent(AttributeKey.EXCEPTION_EVENT.getKey(), attributeMap);
              throw wrap(e);
            } catch (InterruptedException e) {
              span.setAttribute("error", true);
              span.setStatus(Status.NOT_FOUND);
              EXCEPTION.accept(attributeMap, e);
              attributeMap.put(AttributeKey.EXCEPTION_MESSAGE.getKey(),
                               EventAttribute.setValue("Unable to get Node information: " + e.getMessage()));
              span.addEvent(AttributeKey.EXCEPTION_EVENT.getKey(), attributeMap);
              Thread.currentThread().interrupt();
              throw wrap(e);
          }
        })
        .collect(toList()));

      HttpResponse res = new HttpResponse().setContent(asJson(ImmutableMap.of("value", value.build())));
      HTTP_RESPONSE.accept(span, res);
      HTTP_RESPONSE_EVENT.accept(attributeMap, res);
      attributeMap.put("grid.status", EventAttribute.setValue(ready));
      span.setStatus(Status.OK);
      span.addEvent("Computed grid status", attributeMap);
      return res;
    }
  }

  private RuntimeException wrap(Exception e) {
    if (e instanceof InterruptedException) {
      Thread.currentThread().interrupt();
      return new RuntimeException(e);
    }

    Throwable cause = e.getCause();
    if (cause == null) {
      return e instanceof RuntimeException ? (RuntimeException) e : new RuntimeException(e);
    }
    return cause instanceof RuntimeException ? (RuntimeException) cause
                                             : new RuntimeException(cause);
  }
}
