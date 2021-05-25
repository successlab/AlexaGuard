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

import org.openqa.selenium.Capabilities;
import org.openqa.selenium.ImmutableCapabilities;
import org.openqa.selenium.NoSuchSessionException;
import org.openqa.selenium.events.EventBus;
import org.openqa.selenium.grid.data.CreateSessionRequest;
import org.openqa.selenium.grid.data.SessionClosedEvent;
import org.openqa.selenium.grid.node.ActiveSession;
import org.openqa.selenium.grid.node.SessionFactory;
import org.openqa.selenium.internal.Require;
import org.openqa.selenium.remote.SessionId;
import org.openqa.selenium.remote.http.HttpHandler;
import org.openqa.selenium.remote.http.HttpRequest;
import org.openqa.selenium.remote.http.HttpResponse;

import java.io.UncheckedIOException;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.logging.Level;
import java.util.logging.Logger;

public class SessionSlot implements
    HttpHandler,
    Function<CreateSessionRequest, Optional<ActiveSession>>,
    Predicate<Capabilities>  {

  private static final Logger LOG = Logger.getLogger(SessionSlot.class.getName());
  private final EventBus bus;
  private final UUID id;
  private final Capabilities stereotype;
  private final SessionFactory factory;
  private final AtomicBoolean reserved = new AtomicBoolean(false);
  private ActiveSession currentSession;

  public SessionSlot(EventBus bus, Capabilities stereotype, SessionFactory factory) {
    this.bus = Require.nonNull("Event bus", bus);
    this.id = UUID.randomUUID();
    this.stereotype = ImmutableCapabilities.copyOf(Require.nonNull("Stereotype", stereotype));
    this.factory = Require.nonNull("Session factory", factory);
  }

  public UUID getId() {
    return id;
  }

  public Capabilities getStereotype() {
    return stereotype;
  }

  public void reserve() {
    if (reserved.getAndSet(true)) {
      throw new IllegalStateException("Attempt to reserve a slot that is already reserved");
    }
  }

  public void release() {
    reserved.set(false);
  }

  public boolean isAvailable() {
    return !reserved.get();
  }

  public ActiveSession getSession() {
    if (isAvailable()) {
      throw new NoSuchSessionException("Session is not running");
    }

    return currentSession;
  }

  public void stop() {
    if (isAvailable()) {
      return;
    }

    SessionId id = currentSession.getId();
    try {
      currentSession.stop();
    } catch (Exception e) {
      LOG.log(Level.WARNING, "Unable to cleanly close session", e);
    }
    currentSession = null;
    release();
    bus.fire(new SessionClosedEvent(id));
  }

  @Override
  public HttpResponse execute(HttpRequest req) throws UncheckedIOException {
    if (currentSession == null) {
      throw new NoSuchSessionException("No session currently running: " + req.getUri());
    }

    return currentSession.execute(req);
  }

  @Override
  public boolean test(Capabilities capabilities) {
    return factory.test(capabilities);
  }

  @Override
  public Optional<ActiveSession> apply(CreateSessionRequest sessionRequest) {
    if (currentSession != null) {
      return Optional.empty();
    }

    if (!test(sessionRequest.getCapabilities())) {
      return Optional.empty();
    }

    try {
      Optional<ActiveSession> possibleSession = factory.apply(sessionRequest);
      possibleSession.ifPresent(session -> currentSession = session);
      return possibleSession;
    } catch (Exception e) {
      LOG.log(Level.WARNING, "Unable to create session", e);
      return Optional.empty();
    }
  }
}
