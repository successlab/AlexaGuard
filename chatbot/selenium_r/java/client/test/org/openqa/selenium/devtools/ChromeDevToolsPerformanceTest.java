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

import org.junit.Assert;
import org.junit.Test;
import org.openqa.selenium.devtools.v84.performance.Performance;
import org.openqa.selenium.devtools.v84.performance.model.Metric;
import org.openqa.selenium.testing.Ignore;

import java.util.List;
import java.util.Objects;
import java.util.Optional;

import static org.openqa.selenium.devtools.v84.performance.Performance.disable;
import static org.openqa.selenium.devtools.v84.performance.Performance.enable;
import static org.openqa.selenium.devtools.v84.performance.Performance.getMetrics;
import static org.openqa.selenium.testing.drivers.Browser.FIREFOX;

@Ignore(FIREFOX)
public class ChromeDevToolsPerformanceTest extends DevToolsTestBase {


  @Test
  public void enableAndDisablePerformance() {
    devTools.send(enable(Optional.empty()));
    driver.get(appServer.whereIs("simpleTest.html"));
    devTools.send(disable());
  }

  @Test
  public void disablePerformance() {
    devTools.send(disable());
    driver.get(appServer.whereIs("simpleTest.html"));
    devTools.send(disable());
  }

  @Test
  public void setTimeDomainTimeTickPerformance() {
    devTools.send(disable());

    devTools.send(Performance.setTimeDomain(Performance.SetTimeDomainTimeDomain.TIMETICKS));
    devTools.send(enable(Optional.empty()));
    driver.get(appServer.whereIs("simpleTest.html"));
    devTools.send(disable());
  }

  @Test
  public void setTimeDomainsThreadTicksPerformance() {
    devTools.send(disable());
    devTools.send(Performance.setTimeDomain(Performance.SetTimeDomainTimeDomain.THREADTICKS));
    devTools.send(enable(Optional.empty()));
    driver.get(appServer.whereIs("simpleTest.html"));
    devTools.send(disable());
  }

  @Test
  public void getMetricsByTimeTicks() {
    devTools.send(Performance.setTimeDomain(Performance.SetTimeDomainTimeDomain.TIMETICKS));
    devTools.send(enable(Optional.empty()));
    driver.get(appServer.whereIs("simpleTest.html"));
    List<Metric> metrics = devTools.send(getMetrics());
    Objects.requireNonNull(metrics);
    Assert.assertFalse(metrics.isEmpty());
    devTools.send(disable());
  }

  @Test
  public void getMetricsByThreadTicks() {
    devTools.send(Performance.setTimeDomain(Performance.SetTimeDomainTimeDomain.THREADTICKS));
    devTools.send(enable(Optional.empty()));
    driver.get(appServer.whereIs("simpleTest.html"));
    List<Metric> metrics = devTools.send(getMetrics());
    Objects.requireNonNull(metrics);
    Assert.assertFalse(metrics.isEmpty());
    devTools.send(disable());
  }


}
