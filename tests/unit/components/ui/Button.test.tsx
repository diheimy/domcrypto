/**
 * Tests para componente Button
 * Seguindo QA-SPEC.md
 */

import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from '@/components/ui/button'

describe('Button', () => {
  it('deve renderizar botão com texto', () => {
    render(<Button>Clique aqui</Button>)

    expect(screen.getByRole('button', { name: /clique aqui/i })).toBeInTheDocument()
  })

  it('deve chamar onClick ao clicar', async () => {
    const handleClick = jest.fn()
    render(
      <Button onClick={handleClick}>
        Clique aqui
      </Button>
    )

    await userEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('deve renderizar variante primary', () => {
    render(<Button variant="primary">Primary</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('bg-gold')
  })

  it('deve renderizar variante secondary', () => {
    render(<Button variant="secondary">Secondary</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('border-gold')
    expect(button).toHaveClass('text-gold')
  })

  it('deve renderizar variante ghost', () => {
    render(<Button variant="ghost">Ghost</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('hover:bg-hover')
  })

  it('deve renderizar variante danger', () => {
    render(<Button variant="danger">Danger</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('bg-red/20')
    expect(button).toHaveClass('text-red')
  })

  it('deve renderizar variante outline', () => {
    render(<Button variant="outline">Outline</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('border')
    expect(button).toHaveClass('border-border')
  })

  it('deve renderizar tamanho sm', () => {
    render(<Button size="sm">Small</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('h-8')
    expect(button).toHaveClass('px-3')
  })

  it('deve renderizar tamanho md', () => {
    render(<Button size="md">Base</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('h-10')
    expect(button).toHaveClass('px-4')
  })

  it('deve renderizar tamanho lg', () => {
    render(<Button size="lg">Large</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('h-12')
    expect(button).toHaveClass('px-6')
  })

  it('deve renderizar botão disabled', () => {
    render(<Button disabled>Disabled</Button>)

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })

  it('deve renderizar como link quando asChild=true', () => {
    render(
      <Button asChild>
        <a href="/test">Link</a>
      </Button>
    )

    expect(screen.getByRole('link')).toBeInTheDocument()
  })

  it('deve aplicar className customizada', () => {
    render(<Button className="custom-class">Custom</Button>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('custom-class')
  })

  it('deve renderizar children sem variant quando children é string', () => {
    render(<Button>Test</Button>)

    expect(screen.getByText('Test')).toBeInTheDocument()
  })
})
