import '@testing-library/jest-dom'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
    }
  },
  usePathname() {
    return '/mock-path'
  },
  useSearchParams() {
    return new URLSearchParams()
  },
}))

// Mock EventSource for SSE tests
const mockEventSource = {
  close: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
}

Object.defineProperty(window, 'EventSource', {
  writable: true,
  value: jest.fn().mockImplementation(() => mockEventSource),
})

// Mock fetch
global.fetch = jest.fn()

// Cleanup after each test
afterEach(() => {
  jest.clearAllMocks()
  jest.restoreAllMocks()
})
