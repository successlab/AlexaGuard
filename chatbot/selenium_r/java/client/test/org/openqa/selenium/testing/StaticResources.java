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

package org.openqa.selenium.testing;

import static org.openqa.selenium.build.DevMode.isInDevMode;

import org.openqa.selenium.build.BazelBuild;
import org.openqa.selenium.build.InProject;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Objects;
import java.util.logging.Logger;

class StaticResources {
  private static Logger log = Logger.getLogger(StaticResources.class.getName());

  static void ensureAvailable() {
    if (!isInDevMode()) {
      // we should only need to do this when we're in dev mode
      // when running in a test suite, our dependencies should already
      // be listed.
      log.info("Not in dev mode. Ignoring attempt to copy static resources");
      return;
    }

    if (!Files.exists(InProject.findProjectRoot().resolve("Rakefile"))) {
      // we're not in dev mode
      return;
    }

    System.out.println("Copying resources");

    BazelBuild bazel = new BazelBuild();

    // W3C emulation
    bazel.build("//javascript/atoms/fragments:is-displayed");
    copy("javascript/atoms/fragments/is-displayed.js",
         "org/openqa/selenium/remote/isDisplayed.js");
    bazel.build("//javascript/webdriver/atoms:get-attribute");
    copy("javascript/webdriver/atoms/get-attribute.js",
         "org/openqa/selenium/remote/getAttribute.js");

    // Relative locators
    bazel.build("//javascript/atoms/fragments:find-elements");
    copy("javascript/atoms/fragments/find-elements.js",
         "org/openqa/selenium/support/locators/findElements.js");

    // Firefox XPI
    copy("third_party/js/selenium/webdriver_prefs.json",
         "org/openqa/selenium/firefox/webdriver_prefs.json");
    bazel.build("third_party/js/selenium:webdriver_xpi");
    copy("third_party/js/selenium/webdriver.xpi",
        "org/openqa/selenium/firefox/xpi/webdriver.xpi");
  }

  private static void copy(String copyFrom, String copyTo) {
    try {
      Path source = InProject.locate("bazel-bin").resolve(copyFrom);
      Path dest = InProject.locate("java/build/test").resolve(copyTo);

      if (Files.exists(dest)) {
        // Assume we're good.
        return;
      }

      Files.createDirectories(dest.getParent());
      Files.copy(source, dest);
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    }
  }

}
