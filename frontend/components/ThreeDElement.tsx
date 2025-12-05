import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Environment, MeshDistortMaterial, RoundedBox, OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

const FoldedSweater = () => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (meshRef.current) {
      // Gentle floating rotation
      meshRef.current.rotation.y = Math.sin(t * 0.2) * 0.1; 
      meshRef.current.rotation.z = Math.sin(t * 0.15) * 0.05;
    }
  });

  return (
    <Float 
      speed={2} 
      rotationIntensity={0.5} 
      floatIntensity={1} 
      floatingRange={[0, 0.5]}
    >
      <group rotation={[0.5, -0.5, 0]}> {/* Angled slightly to the left/down to show volume */}
        <RoundedBox 
          ref={meshRef}
          args={[3.5, 4, 1.2]} // Dimensions resembling a folded shirt/sweater
          radius={0.4} // Soft rounded corners like fabric
          smoothness={4}
        >
          <MeshDistortMaterial
            color="#6366f1" // Indigo/Sweater color
            envMapIntensity={1}
            clearcoat={0}
            clearcoatRoughness={1}
            metalness={0.1}
            roughness={0.8} // High roughness for fabric texture
            distort={0.15} // Slight distortion to make it look organic/not perfect geometry
            speed={1}
          />
        </RoundedBox>
      </group>
    </Float>
  );
};

export const ThreeDElement: React.FC = () => {
  return (
    <div className="w-full h-full cursor-grab active:cursor-grabbing">
      <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
        {/* Lights */}
        <ambientLight intensity={0.8} />
        <spotLight 
          position={[10, 10, 10]} 
          angle={0.15} 
          penumbra={1} 
          intensity={1.5} 
          castShadow 
        />
        <pointLight position={[-10, -5, -10]} intensity={0.5} color="#eef2ff" />
        
        {/* The Object */}
        <FoldedSweater />
        
        {/* Environment Reflections */}
        <Environment preset="city" />

        {/* User Interaction Controls */}
        <OrbitControls 
          enableZoom={false} 
          enablePan={false}
          minPolarAngle={Math.PI / 3}
          maxPolarAngle={Math.PI / 1.5}
        />
      </Canvas>
    </div>
  );
};