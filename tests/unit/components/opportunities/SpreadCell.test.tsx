/**
 * Tests para componente SpreadCell
 * Seguindo QA-SPEC.md
 */

import React from 'react'
import { render, screen } from '@testing-library/react'
import { SpreadCell } from '@/components/opportunities/SpreadCell'

describe('SpreadCell', () => {
  it('deve renderizar spread positivo em verde', () => {
    render(<SpreadCell spread_net_pct={1.5} />)

    const spread = screen.getByText('+1.50%')
    expect(spread).toBeInTheDocument()
    expect(spread).toHaveClass('text-green')
  })

  it('deve renderizar spread negativo em vermelho', () => {
    render(<SpreadCell spread_net_pct={-0.5} />)

    const spread = screen.getByText('-0.50%')
    expect(spread).toBeInTheDocument()
    expect(spread).toHaveClass('text-red')
  })

  it('deve renderizar spread zero em muted', () => {
    render(<SpreadCell spread_net_pct={0} />)

    const spread = screen.getByText('+0.00%')
    expect(spread).toBeInTheDocument()
    expect(spread).toHaveClass('text-muted')
  })

  it('deve formatar spread com 2 casas decimais', () => {
    render(<SpreadCell spread_net_pct={1.25} />)

    expect(screen.getByText('+1.25%')).toBeInTheDocument()
  })

  it('deve mostrar spread bruto quando showGross=true', () => {
    render(
      <SpreadCell
        spread_net_pct={1.5}
        spread_exec_pct={2.0}
        showGross
      />
    )

    expect(screen.getByText('Gross: +2.00%')).toBeInTheDocument()
  })

  it('não deve mostrar spread bruto quando showGross=false (default)', () => {
    render(
      <SpreadCell
        spread_net_pct={1.5}
        spread_exec_pct={2.0}
      />
    )

    expect(screen.queryByText(/Gross:/)).not.toBeInTheDocument()
  })

  it('não deve mostrar spread bruto quando spread_exec_pct é undefined', () => {
    render(
      <SpreadCell
        spread_net_pct={1.5}
        spread_exec_pct={undefined}
        showGross
      />
    )

    expect(screen.queryByText(/Gross:/)).not.toBeInTheDocument()
  })

  it('deve renderizar em coluna flex', () => {
    render(<SpreadCell spread_net_pct={1.5} />)

    const container = screen.getByText('+1.50%').closest('div')
    expect(container).toHaveClass('flex')
    expect(container).toHaveClass('flex-col')
  })

  it('deve aplicar font-bold ao spread', () => {
    render(<SpreadCell spread_net_pct={1.5} />)

    const spread = screen.getByText('+1.50%')
    expect(spread).toHaveClass('font-bold')
  })

  it('deve aplicar font-mono ao spread bruto', () => {
    render(
      <SpreadCell
        spread_net_pct={1.5}
        spread_exec_pct={2.0}
        showGross
      />
    )

    const gross = screen.getByText('Gross: +2.00%')
    expect(gross).toHaveClass('font-mono')
    expect(gross).toHaveClass('text-xs')
  })

  it('deve lidar com spread percentual muito pequeno', () => {
    render(<SpreadCell spread_net_pct={0.01} />)

    expect(screen.getByText('+0.01%')).toBeInTheDocument()
  })

  it('deve lidar com spread percentual grande', () => {
    render(<SpreadCell spread_net_pct={10.5} />)

    expect(screen.getByText('+10.50%')).toBeInTheDocument()
    expect(screen.getByText('+10.50%')).toHaveClass('text-green')
  })
})
