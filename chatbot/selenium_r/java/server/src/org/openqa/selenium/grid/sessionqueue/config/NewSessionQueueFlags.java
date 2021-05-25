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

package org.openqa.selenium.grid.sessionqueue.config;

import static org.openqa.selenium.grid.config.StandardGridRoles.SESSION_QUEUE_ROLE;

import com.google.auto.service.AutoService;

import com.beust.jcommander.Parameter;

import org.openqa.selenium.grid.config.ConfigValue;
import org.openqa.selenium.grid.config.HasRoles;
import org.openqa.selenium.grid.config.Role;

import java.util.Collections;
import java.util.Set;

@AutoService(HasRoles.class)
public class NewSessionQueueFlags implements HasRoles {

  @Parameter(
    names = { "--session-request-timeout" },
    description = "Timeout in seconds. New incoming session request is added to the queue. "
      + "Requests sitting in the queue for longer than the configured time will timeout.")
  @ConfigValue(section = "sessionqueue", name = "session-request-timeout", example = "5")
  private int sessionRequestTimeout = 300;

  @Parameter(
    names = { "--session-retry-interval" },
    description = "Retry interval in seconds. If all slots are busy, new session request " +
      "will be retried after the given interval.")
  @ConfigValue(section = "sessionqueue", name = "session-retry-interval", example = "5")
  private int sessionRetryInterval = 5;

  @Override
  public Set<Role> getRoles() {
    return Collections.singleton(SESSION_QUEUE_ROLE);
  }
}
