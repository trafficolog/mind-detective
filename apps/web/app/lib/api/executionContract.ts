import metadata from '~/generated/localExecution.meta.json'
import type { ExecutionIdentity } from './contracts'

export const EXECUTION_IDENTITY: Readonly<ExecutionIdentity> = Object.freeze({
  version: metadata.version,
  kernel_sha256: metadata.kernel_sha256,
  generated_sha256: metadata.generated_sha256,
  generator_version: metadata.generator_version,
})

export const EXECUTION_CONTRACT_MISMATCH = 'MD_WEB_EXECUTION_CONTRACT_MISMATCH'
