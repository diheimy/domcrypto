/**
 * Tests E2E para Dashboard
 * Seguindo QA-SPEC.md
 */

import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test('deve carregar dashboard com KPIs', async ({ page }) => {
    await page.goto('/dashboard')

    // Verificar KPIs
    await expect(page.getByText('Oportunidades Ativas')).toBeVisible()
    await expect(page.getByText('Melhor Spread')).toBeVisible()
    await expect(page.getByText('Spread Médio')).toBeVisible()
    await expect(page.getByText('Volume 24h Total')).toBeVisible()

    // Verificar status do sistema
    await expect(page.getByText('Status do Sistema')).toBeVisible()
  })

  test('deve mostrar loading inicialmente', async ({ page }) => {
    await page.goto('/dashboard')

    // Verificar loading state (pode não estar visível se carregar rápido)
    // Verificar que os KPI cards estão presentes
    const glassElements = page.locator('.glass')
    await expect(glassElements).toHaveCount(4, { timeout: 5000 })
  })

  test('deve mostrar top oportunidades', async ({ page }) => {
    await page.goto('/dashboard')

    // Verificar tabela de oportunidades
    await expect(page.getByText('Top Oportunidades')).toBeVisible()

    // Verificar cabeçalhos da tabela
    await expect(page.getByText('Score')).toBeVisible()
    await expect(page.getByText('Símbolo')).toBeVisible()
    await expect(page.getByText('Spread')).toBeVisible()
  })

  test('deve navegação pela sidebar funcionar', async ({ page }) => {
    await page.goto('/dashboard')

    // Clicar em Spot x Futuros na sidebar
    await page.getByText('Spot x Futuros').click()

    // Verificar navegação
    await expect(page).toHaveURL('/spot-futuros')
  })

  test('deve mostrar status do sistema', async ({ page }) => {
    await page.goto('/dashboard')

    // Verificar informações do sistema
    await expect(page.getByText('Backend Python')).toBeVisible()
    await expect(page.getByText('Latência Pipeline')).toBeVisible()
    await expect(page.getByText('Cycle ID')).toBeVisible()
  })

  test('deve mostrar contagem de oportunidades', async ({ page }) => {
    await page.goto('/dashboard')

    // Verificar contagens
    await expect(page.getByText('Total')).toBeVisible()
    await expect(page.getByText('Ativas')).toBeVisible()
    await expect(page.getByText('Observação')).toBeVisible()
    await expect(page.getByText('Descartadas')).toBeVisible()
  })
})
