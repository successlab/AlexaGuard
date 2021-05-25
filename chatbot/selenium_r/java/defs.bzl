load(
  "@rules_java//java:defs.bzl",
  _java_binary = "java_binary",
  _java_import = "java_import",
  _java_test = "java_test")
load("//java/private:dist_zip.bzl", _java_dist_zip = "java_dist_zip")
load("//java/private:library.bzl", _java_export = "java_export", _java_library = "java_library")
load("//java/private:javadoc.bzl", _javadoc = "javadoc")
load("//java/private:module.bzl", _java_module = "java_module")
load("//java/private:spotbugs_config.bzl", _spotbugs_config = "spotbugs_config")
load("//java/private:test.bzl", _java_selenium_test_suite = "java_selenium_test_suite", _java_test_suite = "java_test_suite")

java_binary = _java_binary
java_dist_zip = _java_dist_zip
java_export = _java_export
java_import = _java_import
java_library = _java_library
java_module = _java_module
java_selenium_test_suite = _java_selenium_test_suite
java_test = _java_test
java_test_suite = _java_test_suite
javadoc = _javadoc
spotbugs_config = _spotbugs_config
