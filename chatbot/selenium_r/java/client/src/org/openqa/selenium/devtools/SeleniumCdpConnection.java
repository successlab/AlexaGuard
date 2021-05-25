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

package org.openqa.selenium.devtools;

import org.openqa.selenium.Capabilities;
import org.openqa.selenium.HasCapabilities;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.internal.Require;
import org.openqa.selenium.remote.http.ClientConfig;
import org.openqa.selenium.remote.http.HttpClient;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.Map;
import java.util.Optional;

public class SeleniumCdpConnection extends Connection {

  private SeleniumCdpConnection(HttpClient client, String url) {
    super(client, url);
  }

  public static Optional<Connection> create(WebDriver driver) {
    if (!(driver instanceof HasCapabilities)) {
      throw new IllegalStateException("Given webdriver instance must have capabilities");
    }

    return create(((HasCapabilities) driver).getCapabilities());
  }

  public static Optional<Connection> create(Capabilities capabilities) {
    Require.nonNull("Capabilities", capabilities);
    return create(HttpClient.Factory.createDefault(), capabilities);
  }

  public static Optional<Connection> create(HttpClient.Factory clientFactory, Capabilities capabilities) {
    Require.nonNull("HTTP client factory", clientFactory);
    Require.nonNull("Capabilities", capabilities);

    return getCdpUri(capabilities).map(uri -> new SeleniumCdpConnection(
      clientFactory.createClient(ClientConfig.defaultConfig().baseUri(uri)),
      uri.toString()));
  }

  public static Optional<URI> getCdpUri(Capabilities capabilities) {
    Object options = capabilities.getCapability("se:options");

    if (!(options instanceof Map)) {
      return Optional.empty();
    }

    Object cdp = ((Map<?, ?>) options).get("cdp");
    if (!(cdp instanceof String)) {
      return Optional.empty();
    }

    try {
      return Optional.of(new URI((String) cdp));
    } catch (URISyntaxException e) {
      return Optional.empty();
    }
  }
}
