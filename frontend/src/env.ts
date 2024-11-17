declare global {
  interface Window {
    env: any
  }
}

// change with your own variables
type EnvType = {
  REACT_APP_API_HOST: string,
}
export const env: EnvType = { ...process.env, ...window.env }
