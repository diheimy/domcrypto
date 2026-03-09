/**
 * Tests para componente ScoreBadge
 * Seguindo QA-SPEC.md
 */

import React from 'react'
import { render, screen } from '@testing-library/react'
import { ScoreBadge } from '@/components/opportunities/ScoreBadge'

describe('ScoreBadge', () => {
  it('deve renderizar badge com score alto (verde)', () => {
    render(<ScoreBadge score={85} />)

    const badge = screen.getByText('85')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('text-green')
  })

  it('deve renderizar badge com score médio (amarelo)', () => {
    render(<ScoreBadge score={60} />)

    const badge = screen.getByText('60')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('text-yellow-500')
  })

  it('deve renderizar badge com score baixo (vermelho)', () => {
    render(<ScoreBadge score={30} />)

    const badge = screen.getByText('30')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('text-red')
  })

  it('deve renderizar score com limite superior (70)', () => {
    render(<ScoreBadge score={70} />)

    const badge = screen.getByText('70')
    expect(badge).toHaveClass('text-green')
  })

  it('deve renderizar score com limite inferior para médio (69)', () => {
    render(<ScoreBadge score={69} />)

    const badge = screen.getByText('69')
    expect(badge).toHaveClass('text-yellow-500')
  })

  it('deve renderizar score com limite inferior para baixo (49)', () => {
    render(<ScoreBadge score={49} />)

    const badge = screen.getByText('49')
    expect(badge).toHaveClass('text-red')
  })

  it('deve aplicar classe de background corretamente', () => {
    const { rerender } = render(<ScoreBadge score={80} />)

    expect(screen.getByText('80')).toHaveClass('bg-green/20')

    rerender(<ScoreBadge score={50} />)
    expect(screen.getByText('50')).toHaveClass('bg-yellow-500/20')

    rerender(<ScoreBadge score={20} />)
    expect(screen.getByText('20')).toHaveClass('bg-red/20')
  })

  it('deve renderizar com fonte mono', () => {
    render(<ScoreBadge score={75} />)

    const badge = screen.getByText('75')
    expect(badge).toHaveClass('font-mono')
  })

  it('deve aplicar classes de rounded e padding', () => {
    render(<ScoreBadge score={75} />)

    const badge = screen.getByText('75')
    expect(badge).toHaveClass('rounded')
  })

  it('deve aplicar font-bold', () => {
    render(<ScoreBadge score={75} />)

    const badge = screen.getByText('75')
    expect(badge).toHaveClass('font-bold')
  })

  it('deve lidar com score zero', () => {
    render(<ScoreBadge score={0} />)

    const badge = screen.getByText('0')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('text-red')
  })

  it('deve lidar com score máximo (100)', () => {
    render(<ScoreBadge score={100} />)

    const badge = screen.getByText('100')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('text-green')
    expect(badge).toHaveClass('font-bold')
  })

  it('deve renderizar com tamanho sm', () => {
    render(<ScoreBadge score={75} size="sm" />)

    const badge = screen.getByText('75')
    expect(badge).toHaveClass('text-xs')
  })

  it('deve renderizar com tamanho lg', () => {
    render(<ScoreBadge score={75} size="lg" />)

    const badge = screen.getByText('75')
    expect(badge).toHaveClass('text-base')
  })

  it('deve mostrar qualidade quando showQuality=true', () => {
    render(<ScoreBadge score={85} showQuality />)

    expect(screen.getByText('HIGH')).toBeInTheDocument()
  })

  it('não deve mostrar qualidade quando showQuality=false (default)', () => {
    render(<ScoreBadge score={85} />)

    expect(screen.queryByText('HIGH')).not.toBeInTheDocument()
  })
})
