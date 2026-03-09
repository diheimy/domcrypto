/**
 * Tests para componente KpiCard
 * Seguindo QA-SPEC.md
 */

import React from 'react'
import { render, screen } from '@testing-library/react'
import { TrendingUp, DollarSign } from 'lucide-react'
import { KpiCard } from '@/components/dashboard/KpiCard'

describe('KpiCard', () => {
  const defaultProps = {
    title: 'Oportunidades Ativas',
    value: 12,
    icon: <TrendingUp data-testid="icon" />,
  }

  it('deve renderizar o KpiCard corretamente', () => {
    render(<KpiCard {...defaultProps} />)

    expect(screen.getByText('Oportunidades Ativas')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
    expect(screen.getByTestId('icon')).toBeInTheDocument()
  })

  it('deve renderizar valor como string', () => {
    render(
      <KpiCard
        title="Melhor Spread"
        value="+1.50%"
        icon={<DollarSign data-testid="icon" />}
      />
    )

    expect(screen.getByText('+1.50%')).toBeInTheDocument()
  })

  it('deve renderizar cambio com trend up', () => {
    render(
      <KpiCard
        {...defaultProps}
        change="+5%"
        trend="up"
        icon={<TrendingUp data-testid="icon" />}
      />
    )

    // O container do change tem a classe text-green
    const changeContainer = screen.getByText('+5%').parentElement
    expect(changeContainer).toHaveClass('text-green')
  })

  it('deve renderizar cambio com trend down', () => {
    render(
      <KpiCard
        {...defaultProps}
        change="-3%"
        trend="down"
        icon={<TrendingUp data-testid="icon" />}
      />
    )

    // O container do change tem a classe text-red
    const changeContainer = screen.getByText('-3%').parentElement
    expect(changeContainer).toHaveClass('text-red')
  })

  it('deve renderizar cambio com trend neutral', () => {
    render(
      <KpiCard
        {...defaultProps}
        change="0%"
        trend="neutral"
        icon={<TrendingUp data-testid="icon" />}
      />
    )

    const change = screen.getByText('0%')
    // Trend neutral usa cor padrao (white text)
    expect(change).toBeInTheDocument()
  })

  it('não deve renderizar cambio quando não fornecido', () => {
    const { container } = render(<KpiCard {...defaultProps} />)

    expect(container.querySelector('.text-green')).not.toBeInTheDocument()
    expect(container.querySelector('.text-red')).not.toBeInTheDocument()
  })

  it('deve aplicar classes de glassmorphism', () => {
    render(<KpiCard {...defaultProps} />)

    const card = screen.getByText('Oportunidades Ativas').closest('.glass')
    expect(card).toBeInTheDocument()
  })

  it('deve ter borda border-border', () => {
    render(<KpiCard {...defaultProps} />)

    const card = screen.getByText('Oportunidades Ativas').closest('.border-border')
    expect(card).toBeInTheDocument()
  })
})
