/**
 * Tests para utils de formatters
 * Seguindo QA-SPEC.md
 */

import {
  formatUSD,
  formatCurrency,
  formatPercent,
  formatNumber,
  formatTime,
  formatRelativeTime,
  formatFundingRate,
  cn,
  getCapacityColor,
  getCapacityLabel,
  getStatusColor,
  getStatusLabel,
  getScoreColor,
  getScoreBg,
  getScoreQuality,
  getExchangeDisplayName,
  isFuturesExchange,
  isValidOpportunity,
} from '@/utils/formatters'

describe('formatUSD', () => {
  it('deve formatar valores menores que 1000', () => {
    expect(formatUSD(500)).toBe('$500.00')
    expect(formatUSD(99.99)).toBe('$99.99')
  })

  it('deve formatar valores em milhares (K)', () => {
    expect(formatUSD(1500)).toBe('$2K')
    expect(formatUSD(50000)).toBe('$50K')
    expect(formatUSD(999999)).toBe('$1000K')
  })

  it('deve formatar valores em milhões (M)', () => {
    expect(formatUSD(1500000)).toBe('$1.50M')
    expect(formatUSD(5000000)).toBe('$5.00M')
  })

  it('deve lidar com zero', () => {
    expect(formatUSD(0)).toBe('$0.00')
  })
})

describe('formatCurrency', () => {
  it('deve formatar valores como moeda', () => {
    expect(formatCurrency(100)).toBe('$100.00')
    expect(formatCurrency(1000)).toBe('$1K')
    expect(formatCurrency(1000000)).toBe('$1.00M')
  })

  it('deve ser alias de formatUSD', () => {
    expect(formatCurrency(5000)).toBe(formatUSD(5000))
  })
})

describe('formatPercent', () => {
  it('deve formatar percentual com sinal positivo', () => {
    expect(formatPercent(0.5)).toBe('+0.50%')
    expect(formatPercent(1.25)).toBe('+1.25%')
  })

  it('deve formatar percentual com sinal negativo', () => {
    expect(formatPercent(-0.5)).toBe('-0.50%')
    expect(formatPercent(-1.25)).toBe('-1.25%')
  })

  it('deve usar casas decimais customizadas', () => {
    expect(formatPercent(1.5, 4)).toBe('+1.5000%')
  })

  it('deve lidar com zero', () => {
    expect(formatPercent(0)).toBe('+0.00%')
  })
})

describe('formatNumber', () => {
  it('deve formatar números menores que 1000', () => {
    expect(formatNumber(500)).toBe('500')
    expect(formatNumber(99)).toBe('99')
  })

  it('deve formatar números em milhares (K)', () => {
    expect(formatNumber(1500)).toBe('2K')
    expect(formatNumber(50000)).toBe('50K')
  })

  it('deve formatar números em milhões (M)', () => {
    expect(formatNumber(1500000)).toBe('1.50M')
    expect(formatNumber(5000000)).toBe('5.00M')
  })
})

describe('formatTime', () => {
  it('deve formatar timestamp para hora local', () => {
    const timestamp = 1709856000 // 2024-03-08 00:00:00 UTC
    const result = formatTime(timestamp * 1000)
    expect(result).toBeTruthy()
    expect(typeof result).toBe('string')
  })
})

describe('formatRelativeTime', () => {
  it('deve retornar "Agora" para tempo recente', () => {
    const now = Date.now() / 1000
    expect(formatRelativeTime(now - 30)).toBe('Agora')
    expect(formatRelativeTime(now - 59)).toBe('Agora')
  })

  it('deve formatar em minutos', () => {
    const now = Date.now() / 1000
    expect(formatRelativeTime(now - 120)).toBe('2 min atrás')
  })

  it('deve formatar em horas', () => {
    const now = Date.now() / 1000
    expect(formatRelativeTime(now - 7200)).toBe('2 h atrás')
  })

  it('deve formatar em dias', () => {
    const now = Date.now() / 1000
    expect(formatRelativeTime(now - 172800)).toBe('2 d atrás')
  })
})

describe('formatFundingRate', () => {
  it('deve formatar funding rate como percentual', () => {
    expect(formatFundingRate(0.0001)).toBe('0.0100%')
    expect(formatFundingRate(0.01)).toBe('1.0000%')
  })

  it('deve lidar com funding rate negativo', () => {
    expect(formatFundingRate(-0.0001)).toBe('-0.0100%')
  })
})

describe('cn (classNames)', () => {
  it('deve juntar classes', () => {
    expect(cn('class1', 'class2')).toBe('class1 class2')
  })

  it('deve filtrar valores falsy', () => {
    expect(cn('class1', false, undefined, null, '')).toBe('class1')
  })

  it('deve lidar com classes condicionais', () => {
    const isActive = true
    expect(cn('base', isActive && 'active')).toBe('base active')
  })

  it('deve retornar string vazia sem argumentos', () => {
    expect(cn()).toBe('')
  })
})

describe('getCapacityColor', () => {
  it('deve retornar cor verde para GREEN', () => {
    expect(getCapacityColor('GREEN')).toBe('text-green bg-green/20')
  })

  it('deve retornar cor amarela para YELLOW', () => {
    expect(getCapacityColor('YELLOW')).toBe('text-yellow-500 bg-yellow-500/20')
  })

  it('deve retornar cor vermelha para RED', () => {
    expect(getCapacityColor('RED')).toBe('text-red bg-red/20')
  })
})

describe('getCapacityLabel', () => {
  it('deve retornar o label da capacidade', () => {
    expect(getCapacityLabel('GREEN')).toBe('GREEN')
    expect(getCapacityLabel('YELLOW')).toBe('YELLOW')
    expect(getCapacityLabel('RED')).toBe('RED')
  })
})

describe('getStatusColor', () => {
  it('deve retornar cor verde para ACTIVE', () => {
    expect(getStatusColor('ACTIVE')).toBe('text-green bg-green/20')
  })

  it('deve retornar cor verde para READY', () => {
    expect(getStatusColor('READY')).toBe('text-green bg-green/20')
  })

  it('deve retornar cor amarela para OBSERVATION_ONLY', () => {
    expect(getStatusColor('OBSERVATION_ONLY')).toBe('text-yellow-500 bg-yellow-500/20')
  })

  it('deve retornar cor vermelha para KILLED', () => {
    expect(getStatusColor('KILLED')).toBe('text-red bg-red/20')
  })

  it('deve retornar cor muted para DEGRADED', () => {
    expect(getStatusColor('DEGRADED')).toBe('text-muted bg-muted/20')
  })
})

describe('getStatusLabel', () => {
  it('deve retornar labels abreviadas', () => {
    expect(getStatusLabel('ACTIVE')).toBe('ACTIVE')
    expect(getStatusLabel('READY')).toBe('READY')
    expect(getStatusLabel('OBSERVATION_ONLY')).toBe('OBS')
    expect(getStatusLabel('KILLED')).toBe('KILLED')
    expect(getStatusLabel('DEGRADED')).toBe('DEGRADED')
  })
})

describe('getScoreColor', () => {
  it('deve retornar verde para score >= 70', () => {
    expect(getScoreColor(70)).toBe('text-green')
    expect(getScoreColor(100)).toBe('text-green')
  })

  it('deve retornar amarelo para score entre 50 e 69', () => {
    expect(getScoreColor(50)).toBe('text-yellow-500')
    expect(getScoreColor(69)).toBe('text-yellow-500')
  })

  it('deve retornar vermelho para score < 50', () => {
    expect(getScoreColor(49)).toBe('text-red')
    expect(getScoreColor(0)).toBe('text-red')
  })
})

describe('getScoreBg', () => {
  it('deve retornar background verde para score >= 70', () => {
    expect(getScoreBg(70)).toBe('bg-green/20')
  })

  it('deve retornar background amarelo para score entre 50 e 69', () => {
    expect(getScoreBg(50)).toBe('bg-yellow-500/20')
  })

  it('deve retornar background vermelho para score < 50', () => {
    expect(getScoreBg(49)).toBe('bg-red/20')
  })
})

describe('getScoreQuality', () => {
  it('deve retornar HIGH para score >= 70', () => {
    expect(getScoreQuality(70)).toBe('HIGH')
    expect(getScoreQuality(100)).toBe('HIGH')
  })

  it('deve retornar MEDIUM para score entre 50 e 69', () => {
    expect(getScoreQuality(50)).toBe('MEDIUM')
    expect(getScoreQuality(69)).toBe('MEDIUM')
  })

  it('deve retornar LOW para score < 50', () => {
    expect(getScoreQuality(49)).toBe('LOW')
    expect(getScoreQuality(0)).toBe('LOW')
  })
})

describe('getExchangeDisplayName', () => {
  it('deve remover sufixo _futures', () => {
    expect(getExchangeDisplayName('binance_futures')).toBe('binance')
    expect(getExchangeDisplayName('mexc_futures')).toBe('mexc')
  })

  it('deve substituir underscore por espaço', () => {
    expect(getExchangeDisplayName('binance_futures')).toBe('binance')
  })

  it('deve retornar nome original sem sufixo', () => {
    expect(getExchangeDisplayName('binance')).toBe('binance')
  })
})

describe('isFuturesExchange', () => {
  it('deve retornar true para exchanges futures', () => {
    expect(isFuturesExchange('binance_futures')).toBe(true)
    expect(isFuturesExchange('mexc_futures')).toBe(true)
  })

  it('deve retornar false para exchanges spot', () => {
    expect(isFuturesExchange('binance')).toBe(false)
    expect(isFuturesExchange('mexc')).toBe(false)
  })
})

describe('isValidOpportunity', () => {
  it('deve retornar true para oportunidade válida', () => {
    const opp = {
      spread_net_pct: 1.5,
      score: 75,
      volume_24h_usd: 500000,
    }
    expect(isValidOpportunity(opp)).toBe(true)
  })

  it('deve retornar false para spread negativo', () => {
    const opp = {
      spread_net_pct: -0.5,
      score: 75,
      volume_24h_usd: 500000,
    }
    expect(isValidOpportunity(opp)).toBe(false)
  })

  it('deve retornar false para score fora do range', () => {
    const opp1 = {
      spread_net_pct: 1.5,
      score: -10,
      volume_24h_usd: 500000,
    }
    const opp2 = {
      spread_net_pct: 1.5,
      score: 150,
      volume_24h_usd: 500000,
    }
    expect(isValidOpportunity(opp1)).toBe(false)
    expect(isValidOpportunity(opp2)).toBe(false)
  })

  it('deve retornar false para volume negativo', () => {
    const opp = {
      spread_net_pct: 1.5,
      score: 75,
      volume_24h_usd: -1000,
    }
    expect(isValidOpportunity(opp)).toBe(false)
  })
})
