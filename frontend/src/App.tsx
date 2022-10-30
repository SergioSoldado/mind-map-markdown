import React from 'react'
import { useState, useCallback, useEffect } from 'react'
import ReactFlow, {
  addEdge,
  Background,
  FitViewOptions,
  applyNodeChanges,
  applyEdgeChanges,
  Node,
  Edge,
  NodeChange,
  EdgeChange,
  Connection,
  Controls,
} from 'reactflow'
import axios from 'axios'
import { io } from 'socket.io-client'
import 'reactflow/dist/style.css'
import './App.css'

const fitViewOptions: FitViewOptions = {
  padding: 0.2,
}

function App() {
  const [nodes, setNodes] = useState<Node[]>([])
  const [edges, setEdges] = useState<Edge[]>([])
  useEffect(() => {
    const socket = io('localhost:5000/', {
      // reconnection: true,
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
        node.position.x = 1000 + node.position.x * 500
        node.position.y = 1000 + node.position.y * 500
        return node
      })
      setNodes(nodes)
      setEdges(edges)
    })

    return () => {
      socket.off('connect')
      socket.off('disconnect')
      socket.off('pong')
    }
  }, [])

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

  const onNodeClick = (event: React.MouseEvent, node: Node) => {
    console.log(node)
    axios
      .post('http://localhost:5000/onClick', { id: node.id })
      .then((res) => {
        console.log(res)
      })
      .catch((err) => {
        console.log(err)
      })
  }

  return (
    <ReactFlow
      className="App"
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      onNodeClick={onNodeClick}
      fitView
      fitViewOptions={fitViewOptions}
    >
      <Controls />
      {/*// @ts-ignore*/}
      {/*<Background variant="dots" color="#000" gap={16} />*/}
    </ReactFlow>
  )
}

export default App
