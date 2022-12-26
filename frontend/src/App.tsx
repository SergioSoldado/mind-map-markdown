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
  Controls,
} from 'reactflow'
import axios from 'axios'
import { io } from 'socket.io-client'
import 'reactflow/dist/style.css'
import Slider from './components/Slider'
import Select from './components/Select'
import './App.css'
import { GraphOptions } from './api'

import styled from 'styled-components'

const FixMe = styled.div`
  position: fixed;
  right: 1rem;
  bottom: 2rem;
  z-index: 1000;
`

const fitViewOptions: FitViewOptions = {
  padding: 0.2,
}

function App() {
  const [controls, setControls] = useState<GraphOptions>({
    depth: 2,
    layout: 'spring',
  })
  const [nodes, setNodes] = useState<Node[]>([])
  const [edges, setEdges] = useState<Edge[]>([])

  useEffect(() => {
    const socket = io('localhost:5000/', {
      // reconnection: true,
      // transports: ["websocket"]
    })

    socket.on('connect', () => {
      console.log('Connected')
      axios.post('http://localhost:5000/graph/controls', controls).then(null)
    })

    socket.on('disconnect', (data) => {
      console.log(data)
    })

    socket.on('graph', (data) => {
      console.log(data)
      const edges: Edge[] = data.edges
      const nodes: Node[] = data.nodes.map((node: Node) => {
        node.position.x = 2000 + node.position.x * 1500
        node.position.y = 2000 + node.position.y * 1500
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

  const onSliderChange = (value: number) => {
    console.log(value)
    setControls({ ...controls, depth: value })
  }

  const onLayoutChange = (value: string) => {
    console.log(value)
    setControls({ ...controls, layout: value })
  }

  useEffect(() => {
    axios.post('http://localhost:5000/graph/controls', controls).then(null)
  }, [controls])

  return (
    <>
      <FixMe>
        <Select
          label="layout"
          options={[
            'spring',
            'kamada_kawai',
            'circular',
            'bipartite',
            'spectral',
            'shell',
            'fruchterman_reingold',
          ]}
          onEvent={onLayoutChange}
        />
        <Slider onEvent={onSliderChange} maxSteps={5} />
      </FixMe>
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
    </>
  )
}

export default App
