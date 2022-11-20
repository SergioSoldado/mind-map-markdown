/*
This code comes from https://joshwcomeau.com/gatsby/dark-mode/
It uses the users' prefers-color-scheme media query to inline
CSS variables into the :root of the page before any content is
rendered.

ToDo: Check out https://janosh.io/blog/use-dark-mode
*/
import * as React from 'react'
import Terser from 'terser'
import { COLORS } from './colors'

const magicString = '🌈'

export function setColorsByTheme(): void {
  const colors: string = magicString

  const mql = window.matchMedia('(prefers-color-scheme: dark)')
  const prefersDarkFromMQ = mql.matches
  const colorMode: string = prefersDarkFromMQ ? 'dark' : 'light'

  const root = document.documentElement

  Object.entries(colors).forEach(([name, colorByTheme]) => {
    console.log(`Name:${name} colorByTheme:${colorByTheme}`)
    const cssVarName = `--${name}`
    // @ts-ignore
    root.style.setProperty(cssVarName, colorByTheme[colorMode])
  })
}

export function MagicScriptTag(): JSX.Element {
  const boundFn = String(setColorsByTheme).replace(
    magicString,
    JSON.stringify(COLORS)
  )

  let calledFunction: string | undefined = `(${boundFn})()`

  // @ts-ignore
  calledFunction = Terser.minify(calledFunction).code

  if (calledFunction) {
    return <script dangerouslySetInnerHTML={{ __html: calledFunction }} />
  }
  return <></>
}

// if user doesn't have JavaScript enabled, set variables properly in a
// head style tag anyways (light mode)
export function FallbackStyles(): JSX.Element {
  const cssVariableString = Object.entries(COLORS).reduce(
    (acc, [name, colorByTheme]) => {
      return `${acc}\n--color-${name}: ${colorByTheme.light};`
    },
    ''
  )

  const wrappedInSelector = `html { ${cssVariableString} }`

  return <style>{wrappedInSelector}</style>
}
