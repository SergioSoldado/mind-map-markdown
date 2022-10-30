import React from 'react'
import { useState, useCallback, useEffect } from 'react'
import ReactFlow, {
  addEdge,
  FitViewOptions,
  applyNodeChanges,
  applyEdgeChanges,
  Node,
  Edge,
  NodeChange,
  EdgeChange,
  Connection,
} from 'reactflow'
import { io } from 'socket.io-client'
import './App.css'
import 'reactflow/dist/style.css'

const fitViewOptions: FitViewOptions = {
  padding: 0.2,
}

function App() {
  const [nodes, setNodes] = useState<Node[]>([])
  const [edges, setEdges] = useState<Edge[]>([])
  useEffect(() => {
    const socket = io('localhost:5000/', {
      reconnection: true,
      // transports: ["websocket"]
    })
    socket.on('connect', () => {
      console.log('Connected')
    })

    socket.on('disconnect', (data) => {
      console.log(data)
    })

    socket.on('graph', (data) => {
      console.log(data)
      const edges: Edge[] = data.edges
      const nodes: Node[] = data.nodes.map((node: Node) => {
        node.position.x = 1000 + node.position.x * 1000
        node.position.y = 1000 + node.position.y * 1000
        return node
      })
      setNodes(nodes)
      setEdges(edges)
    })
  })

  const onNodesChange = useCallback(
    (changes: NodeChange[]) =>
      setNodes((nds) => applyNodeChanges(changes, nds)),
    [setNodes]
  )
  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) =>
      setEdges((eds) => applyEdgeChanges(changes, eds)),
    [setEdges]
  )
  const onConnect = useCallback(
    (connection: Connection) => setEdges((eds) => addEdge(connection, eds)),
    [setEdges]
  )

  return (
    <ReactFlow
      className="App"
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      fitView
      fitViewOptions={fitViewOptions}
    />
  )
}

export default App
