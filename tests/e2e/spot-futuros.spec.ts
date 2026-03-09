/**
 * Tests E2E para Spot x Futuros
 * Seguindo QA-SPEC.md
 */

import { test, expect } from '@playwright/test'

test.describe('Spot x Futuros', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/spot-futuros')
  })

  test('deve mostrar tabela de oportunidades', async ({ page }) => {
    // Verificar cabeçalhos da tabela
    await expect(page.getByText('Score')).toBeVisible({ timeout: 10000 })
    await expect(page.getByText('Ativo')).toBeVisible()
    await expect(page.getByText('Spread')).toBeVisible()
    await expect(page.getByText('ROI')).toBeVisible()
    await expect(page.getByText('Exchanges')).toBeVisible()
  })

  test('deve abrir filtro drawer', async ({ page }) => {
    // Clicar em Filtros
    await page.getByText('Filtros').click()

    // Verificar drawer aberto
    await expect(page.getByText('Filtros')).toBeVisible()
    await expect(page.getByText('Spread Mínimo')).toBeVisible()
    await expect(page.getByText('Score Mínimo')).toBeVisible()
  })

  test('deve filtrar por spread mínimo', async ({ page }) => {
    // Abrir filtros
    await page.getByText('Filtros').click()

    // Ajustar spread mínimo usando slider
    const spreadSlider = page.locator('input[type="range"]').first()
    await spreadSlider.fill('2')

    // Fechar drawer
    await page.getByText('Filtros').click()
  })

  test('deve pausar/retomar atualizações', async ({ page }) => {
    // Verificar botão Executando
    await expect(page.getByText('Executando')).toBeVisible({ timeout: 10000 })

    // Clicar em pausar
    await page.getByRole('button', { name: /Executando|Pausado/i }).click()

    // Verificar estado pausado
    await expect(page.getByText('Pausado')).toBeVisible({ timeout: 5000 })
  })

  test('deve buscar por símbolo', async ({ page }) => {
    // Abrir filtros
    await page.getByText('Filtros').click()

    // Digitar busca
    const searchInput = page.locator('input[placeholder*="BTC"]').first()
    await searchInput.fill('BTC')

    // Aguardar filtragem
    await page.waitForTimeout(500)

    // Fechar drawer
    await page.getByText('Filtros').click()
  })

  test('deve mostrar KPI bar', async ({ page }) => {
    // Verificar KPIs
    await expect(page.getByText('Oportunidades Ativas')).toBeVisible({ timeout: 10000 })
    await expect(page.getByText('Melhor Spread')).toBeVisible()
    await expect(page.getByText('Spread Médio')).toBeVisible()
  })

  test('deve mostrar footer com informações', async ({ page }) => {
    // Verificar footer
    await expect(page.getByText(/Total:.*oportunidades/)).toBeVisible({ timeout: 10000 })
    await expect(page.getByText('Cycle ID')).toBeVisible()
  })

  test('deve mostrar status de conexão', async ({ page }) => {
    // Verificar indicador de conexão
    await expect(page.locator('.animate-pulse')).toBeVisible({ timeout: 10000 })
  })
})
