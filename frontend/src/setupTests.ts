// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'
import * as ResizeObserverModule from 'resize-observer-polyfill'
import { setImmediate } from 'timers'
global.ResizeObserver = ResizeObserverModule.default
global.setImmediate = setImmediate
