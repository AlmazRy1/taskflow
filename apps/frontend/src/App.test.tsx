import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

describe('TaskFlow App', () => {
  it('renders title', () => {
    render(<App />)
    expect(screen.getByText(/TaskFlow/)).toBeInTheDocument()
  })
  it('has input for new task', () => {
    render(<App />)
    expect(screen.getByPlaceholderText(/Новая задача/)).toBeInTheDocument()
  })
})
