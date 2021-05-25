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

package org.openqa.selenium.testing.drivers;

import org.openqa.selenium.net.NetworkUtils;
import org.openqa.selenium.net.PortProber;
import org.openqa.selenium.net.UrlChecker;
import org.openqa.selenium.os.CommandLine;

import java.net.MalformedURLException;
import java.net.URL;
import java.util.logging.Logger;
import java.util.stream.Stream;

import static java.util.concurrent.TimeUnit.SECONDS;

public class OutOfProcessSeleniumServer {

  private static final Logger log = Logger.getLogger(OutOfProcessSeleniumServer.class.getName());

  private String baseUrl;
  private CommandLine command;
  @SuppressWarnings("unused")
  private boolean captureLogs = false;

  public void enableLogCapture() {
    captureLogs = true;
  }

  /**
   * Creates an out of process server with log capture enabled.
   *
   * @return The new server.
   */
  public OutOfProcessSeleniumServer start(String mode, String... extraFlags) {
    log.info("Got a request to start a new selenium server");
    if (command != null) {
      log.info("Server already started");
      throw new RuntimeException("Server already started");
    }

    String serverJar = buildServerAndClasspath();

    int port = PortProber.findFreePort();
    String localAddress = new NetworkUtils().getPrivateLocalAddress();
    baseUrl = String.format("http://%s:%d", localAddress, port);

    command = new CommandLine("java", Stream.concat(
        Stream.of("-jar", serverJar, mode, "--port", String.valueOf(port)),
        Stream.of(extraFlags)).toArray(String[]::new));

    command.copyOutputTo(System.err);
    log.info("Starting selenium server: " + command.toString());
    command.executeAsync();

    try {
      URL url = new URL(baseUrl + "/status");
      log.info("Waiting for server status on URL " + url);
      new UrlChecker().waitUntilAvailable(5, SECONDS, url);
      log.info("Server is ready");
    } catch (UrlChecker.TimeoutException e) {
      log.severe("Server failed to start: " + e.getMessage());
      command.destroy();
      log.severe(command.getStdOut());
      command = null;
      throw new RuntimeException(e);
    } catch (MalformedURLException e) {
      throw new RuntimeException(e);
    }

    WebDriverBuilder.addShutdownAction(this::stop);

    return this;
  }

  public void stop() {
    if (command == null) {
      return;
    }
    log.info("Stopping selenium server");
    command.destroy();
    log.info("Selenium server stopped");
    command = null;
  }

  private String buildServerAndClasspath() {
    if (System.getProperty("selenium.browser.remote.path") != null) {
      return System.getProperty("selenium.browser.remote.path");
    }
    throw new AssertionError(
      "Please set the sys property selenium.browser.remote.path to point to the out-of-process selenium server");
  }

  public URL getWebDriverUrl() {
    try {
      return new URL(baseUrl);
    } catch (MalformedURLException e) {
      throw new RuntimeException(e);
    }
  }
}
