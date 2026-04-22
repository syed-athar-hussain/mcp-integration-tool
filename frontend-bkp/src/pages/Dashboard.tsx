import { useState } from 'react'
import { AgentCard } from '../components/AgentCard'
import { InvocationForm } from '../components/InvocationForm'
import { StatusTimeline } from '../components/StatusTimeline'
import { ErrorToast } from '../components/ErrorToast'
import { useAgentInvoke } from '../hooks/useAgentInvoke'

export function Dashboard() {
  const { invoke, status, history, error, clearError } = useAgentInvoke()
  const [task, setTask] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!task.trim()) return
    await invoke(task)
    setTask('')
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-white p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 flex items-center gap-3">
          <span className="text-emerald-400">🧬</span>
          Agentic Developer Workflow Dashboard
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Invocation */}
          <div className="lg:col-span-1">
            <InvocationForm task={task} setTask={setTask} onSubmit={handleSubmit} />
          </div>

          {/* Center: Active Agents */}
          <div className="lg:col-span-1 space-y-6">
            <AgentCard
              title="OpenAI Agent"
              model="gpt-4o"
              status={status.openai}
              lastRun={history[0]?.timestamp}
            />
            <AgentCard
              title="Claude Agent"
              model="claude-3-5-sonnet-20241022"
              status={status.claude}
              lastRun={history[0]?.timestamp}
            />
          </div>

          {/* Right: Timeline + MCP Context */}
          <div className="lg:col-span-1">
            <StatusTimeline history={history} />
          </div>
        </div>

        {error && <ErrorToast message={error} onClose={clearError} />}
      </div>
    </div>
  )
}