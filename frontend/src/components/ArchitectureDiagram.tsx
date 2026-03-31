/**
 * RepoLens 架构流程图组件 (React Flow)
 */
"use client";

import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
} from "reactflow";
import "reactflow/dist/style.css";

// 示例节点数据 (TODO: 替换为实际分析结果)
const initialNodes: Node[] = [
  {
    id: "frontend",
    type: "default",
    position: { x: 250, y: 0 },
    data: { label: "Frontend\nNext.js + React" },
    style: { width: 180, textAlign: "center" },
  },
  {
    id: "backend",
    type: "default",
    position: { x: 250, y: 150 },
    data: { label: "Backend\nFastAPI" },
    style: { width: 180, textAlign: "center" },
  },
  {
    id: "db",
    type: "default",
    position: { x: 100, y: 300 },
    data: { label: "PostgreSQL\n(元数据)" },
    style: { width: 160, textAlign: "center" },
  },
  {
    id: "redis",
    type: "default",
    position: { x: 300, y: 300 },
    data: { label: "Redis\n(缓存/队列)" },
    style: { width: 160, textAlign: "center" },
  },
  {
    id: "qdrant",
    type: "default",
    position: { x: 500, y: 300 },
    data: { label: "Qdrant\n(向量DB)" },
    style: { width: 160, textAlign: "center" },
  },
];

const initialEdges: Edge[] = [
  { id: "e1", source: "frontend", target: "backend", label: "HTTP/SSE" },
  { id: "e2", source: "backend", target: "db" },
  { id: "e3", source: "backend", target: "redis" },
  { id: "e4", source: "backend", target: "qdrant" },
];

export function ArchitectureDiagram() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div style={{ height: 500 }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Controls />
        <Background />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}
