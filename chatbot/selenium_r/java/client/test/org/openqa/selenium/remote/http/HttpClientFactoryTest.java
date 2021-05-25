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

package org.openqa.selenium.remote.http;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatExceptionOfType;

import com.google.auto.service.AutoService;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

public class HttpClientFactoryTest {

  private String oldProperty;

  @Before
  public void storeSystemProperty() {
    oldProperty = System.getProperty("webdriver.http.factory");
  }

  @After
  public void restoreSystemProperty() {
    if (oldProperty != null) {
      System.setProperty("webdriver.http.factory", oldProperty);
    } else {
      System.clearProperty("webdriver.http.factory");
    }
  }

  @Test
  public void canCreateDefaultHttpClientFactory() {
    HttpClient.Factory factory = HttpClient.Factory.createDefault();
    assertThat(factory.getClass().getAnnotation(HttpClientName.class).value()).isEqualTo("netty");
  }

  @Test
  public void canCreateHttpClientFactoryByName() {
    HttpClient.Factory factory = HttpClient.Factory.create("reactor");
    assertThat(factory.getClass().getAnnotation(HttpClientName.class).value()).isEqualTo("reactor");
  }

  @Test
  public void canCreateCustomClientFactoryByName() {
    HttpClient.Factory factory = HttpClient.Factory.create("cheesy");
    assertThat(factory.getClass().getAnnotation(HttpClientName.class).value()).isEqualTo("cheesy");
  }

  @AutoService(HttpClient.Factory.class)
  @HttpClientName("cheesy")
  @SuppressWarnings("unused")
  public static class CheesyFactory implements HttpClient.Factory {
    @Override
    public HttpClient createClient(ClientConfig config) {
      return null;
    }
  }

  @Test
  public void shouldRespectSystemProperties() {
    System.setProperty("webdriver.http.factory", "cheesy");
    HttpClient.Factory factory = HttpClient.Factory.createDefault();
    assertThat(factory.getClass().getAnnotation(HttpClientName.class).value()).isEqualTo("cheesy");
  }

  @Test
  public void shouldNotCreateHttpClientFactoryByInvalidName() {
    assertThatExceptionOfType(IllegalArgumentException.class).isThrownBy(
        () -> HttpClient.Factory.create("orange"));
  }

  @Test
  public void canDetectHttpClientFactoriesWithSameName() {
    assertThatExceptionOfType(IllegalStateException.class).isThrownBy(
        () -> HttpClient.Factory.create("duplicated"));
  }

  @AutoService(HttpClient.Factory.class)
  @HttpClientName("duplicated")
  @SuppressWarnings("unused")
  public static class Factory1 implements HttpClient.Factory {
    @Override
    public HttpClient createClient(ClientConfig config) {
      return null;
    }
  }

  @AutoService(HttpClient.Factory.class)
  @HttpClientName("duplicated")
  @SuppressWarnings("unused")
  public static class Factory2 implements HttpClient.Factory {
    @Override
    public HttpClient createClient(ClientConfig config) {
      return null;
    }
  }

}
