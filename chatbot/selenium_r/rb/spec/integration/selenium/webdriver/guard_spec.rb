# frozen_string_literal: true

# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

require_relative 'spec_helper'

module Selenium
  module WebDriver
    module SpecSupport
      describe Guards, exclusive: {driver: :chrome} do
        describe '#exclude' do
          it 'ignores an unrecognized guard parameter', invalid: {browser: :chrome} do
            # pass
          end

          it 'skips without running', exclude: {browser: :chrome} do
            puts "This code will not get executed"
          end
        end

        describe '#exclusive' do
          it 'skips without running if it does not match', exclusive: {browser: :not_chrome} do
            puts "This code will not get executed"
          end

          it 'does not guard if it does match', exclusive: {browser: :chrome} do
            # pass
          end
        end

        describe '#only' do
          it 'guards when value does not match', only: {browser: :not_chrome} do
            fail
          end

          it 'does not guard when value matches', only: {browser: :chrome} do
            # pass
          end
        end

        describe '#except' do
          it 'guards when value matches and test fails', except: {browser: :chrome} do
            fail
          end

          it 'does not guard when value does not match and test passes', except: {browser: :not_chrome} do
            # pass
          end
        end

        context 'when multiple guards' do
          it 'guards if neither only nor except match and test fails', only: {browser: :not_chrome},
                                                                       except: {browser: :not_chrome} do
            fail
          end

          it 'guards if both only and except match', only: {browser: :chrome},
                                                     except: {browser: :chrome} do
            fail
          end

          it 'guards if except matches and only does not', only: {browser: :not_chrome},
                                                           except: {browser: :chrome} do
            fail
          end

          it 'does not guard if only matches and except does not', only: {browser: :chrome},
                                                                   except: {browser: :not_chrome} do
            # pass
          end
        end

        context 'when array of hashes' do
          it 'guards if any Hash value is satisfied', only: [{browser: :chrome}, {browser: :not_chrome}] do
            fail
          end
        end

        context 'guard messages' do
          it 'gives correct reason with single only excludes', except: [{browser: :chrome, reason: 'bug1'},
                                                                        {browser: :not_chrome, reason: 'bug2'}] do
            fail
          end
        end
      end

      describe Guards::Guard do
        it 'Uses default message' do
          guard = Guards::Guard.new({}, :except)
          expect(guard.message).to eq 'Test guarded; no reason given'
        end

        it 'Creates message from Integer' do
          guard = Guards::Guard.new({reason: 1}, :except)
          expect(guard.message).to eq 'Test guarded; Bug Filed: https://github.com/SeleniumHQ/selenium/issues/1'
        end

        it 'Creates message from Symbol' do
          guard = Guards::Guard.new({reason: :unk}, :except)
          expect(guard.message).to eq 'Test guarded; TODO: Investigate why this is failing and file bug'
        end

        it 'Creates message from String' do
          guard = Guards::Guard.new({reason: "Foo is bad"}, :except)
          expect(guard.message).to eq 'Test guarded; Foo is bad'
        end

        it 'Uses correct message for exclusive' do
          guard = Guards::Guard.new({reason: "Foo is bad"}, :exclusive)
          expect(guard.message).to eq 'Test does not apply to this configuration'
        end

        it 'Uses correct message for exclude' do
          guard = Guards::Guard.new({reason: "Foo is bad"}, :exclude)
          expect(guard.message).to eq 'Test not guarded because it breaks test run; Foo is bad'
        end
      end
    end # SpecSupport
  end # WebDriver
end # Selenium
