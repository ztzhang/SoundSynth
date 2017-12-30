/*
Bullet Continuous Collision Detection and Physics Library
Copyright (c) 2015 Google Inc. http://bulletphysics.org
test
This software is provided 'as-is', without any express or implied warranty.
In no event will the authors be held liable for any damages arising from the use of this software.
Permission is granted to anyone to use this software for any purpose, 
including commercial applications, and to alter it and redistribute it freely, 
subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment in the product documentation would be appreciated but is not required.
2. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
3. This notice may not be removed or altered from any source distribution.
*/



#include "RigidBodyFromObj.h"

#include "btBulletDynamicsCommon.h"
#include "LinearMath/btVector3.h"
#include "LinearMath/btAlignedObjectArray.h" 
#include "../CommonInterfaces/CommonRigidBodyBase.h"

#include "../Utils/b3ResourcePath.h"
#include "Bullet3Common/b3FileUtils.h"
#include "../Importers/ImportObjDemo/LoadMeshFromObj.h"
#include "../OpenGLWindow/GLInstanceGraphicsShape.h"

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include "../Utils/b3Clock.h"
#include "BulletCollision/Gimpact/btGImpactShape.h"
#include "BulletCollision/Gimpact/btGImpactCollisionAlgorithm.h"
#include <sstream>
#include <algorithm>
#include <iterator>

btVector3 convertVertex(const GLInstanceVertex& v) {
    return btVector3(v.xyzw[0], v.xyzw[1], v.xyzw[2]);
}

double gSimulationTime = 0;
char* objectList;
float dist, pitch, yaw, targetPos0, targetPos1, targetPos2;
const char* collisionFileOut = "collision_info.dat";
const char* motionFileOut = "motion_info.dat";
//const char* motionsyncFileOut = "motion_sync.dat";
//const float RESTITUTION = 1.0;

static std::ofstream motionFile (motionFileOut);
static std::ofstream collisionFile (collisionFileOut);
//static std::ofstream motionsyncFile (motionsyncFileOut);


struct RigidBodyFromObjExample : public CommonRigidBodyBase
{
    int m_options;
    
	RigidBodyFromObjExample(struct GUIHelperInterface* helper, int options)
		:CommonRigidBodyBase(helper),
		m_options(options)
	{
	}
	virtual ~RigidBodyFromObjExample(){}
	virtual void initPhysics();
    virtual void exitPhysics();
	virtual void renderScene();
    void resetCamera()
	{
//		float dist = 0.5;
//		float pitch = 30;
//		float yaw = 30;
		m_guiHelper->resetCamera(dist,pitch,yaw,targetPos0,targetPos1,targetPos2);
//        float pos[3];
//        m_guiHelper->getRenderInterface()->getActiveCamera()->getCameraPosition(pos);
        collisionFile << dist << " " << pitch << " " << yaw << " " << targetPos0 << " " << targetPos1 << " " << targetPos2 << std::endl;
//        printf("Camera World Coordinates [%f, %f, %f]\n", pos[0], pos[1], pos[2]);
	}
};


// struct and call back functions added

struct bulletObject {
    int id;
    btRigidBody* body;
    bulletObject(btRigidBody* b, int i) : body(b), id(i){}
};

std::vector<bulletObject*> bodies;

// Call back to set restitution before the solver

//bool callbackFunc(btManifoldPoint& cp, const btCollisionObjectWrapper* obj1, int id1, int index1, const btCollisionObjectWrapper* obj2, int id2, int index2)
//{
//    cp.m_combinedRestitution = RESTITUTION;
//
////    std::cout << "friction is " << cp.m_combinedFriction << std::endl;
////    std::cout << "contact stiffness is " << cp.m_combinedContactStiffness1 << std::endl;
////    std::cout << "spinning friction is " << cp.m_combinedSpinningFriction << std::endl;
////    std::cout << "damping is " << cp.m_combinedContactDamping1 << std::endl;
//
//    return false;
//}


void callBack(btDynamicsWorld *world, btScalar timeStep){
    
    // motion file output continued
    int numObj = world->getNumCollisionObjects();
    for (int i = 0; i < numObj; i++){
        btCollisionObject* obj = world->getCollisionObjectArray()[i];
        if (!obj->isStaticObject())
        {
            btMatrix3x3 objRotation = obj->getWorldTransform().getBasis();
            btVector3 objPosition = obj->getWorldTransform().getOrigin();
            std::cout << "At " << gSimulationTime << "s, object " << ((bulletObject*)obj->getUserPointer())->id << " origin position is [" << objPosition[0] << ", " << objPosition[1] << ", " << objPosition[2] << "]. " << "Rotation matrix: [[" << objRotation[0][0] << " " << objRotation[0][1] << " " << objRotation[0][2] << "] [" <<objRotation[1][0] << " " << objRotation[1][1] << " " << objRotation[1][2] << "] [" << objRotation[2][0] << " " <<  objRotation[2][1] << " " <<  objRotation[2][2] << "]]" << std::endl;
            motionFile << ((bulletObject*)obj->getUserPointer())->id << " " << gSimulationTime << " " << objPosition[0] << " " << objPosition[1] << " " << objPosition[2] << " " << objRotation[0][0] << " " << objRotation[0][1] << " " << objRotation[0][2] << " " <<objRotation[1][0] << " " << objRotation[1][1] << " " << objRotation[1][2] << " " << objRotation[2][0] << " " << objRotation[2][1] << " " <<  objRotation[2][2] << std::endl;
        }
    }
    
    int numManifolds = world->getDispatcher()->getNumManifolds();
    for (int i = 0; i < numManifolds; i++)
    {
        btPersistentManifold* contactManifold =  world->getDispatcher()->getManifoldByIndexInternal(i);
        const btCollisionObject* obA = contactManifold->getBody0();
        const btCollisionObject* obB = contactManifold->getBody1();
        
//        if (!obA->isStaticObject())
//        {
//            btMatrix3x3 obARotation = obA->getWorldTransform().getBasis();
//            btVector3 obAPosition = obA->getWorldTransform().getOrigin();
//            motionsyncFile << ((bulletObject*)obA->getUserPointer())->id << " " << gSimulationTime << " " << obAPosition[0] << " " << obAPosition[1] << " " << obAPosition[2] << " " << obARotation[0][0] << " " << obARotation[0][1] << " " << obARotation[0][2] << " " <<obARotation[1][0] << " " << obARotation[1][1] << " " << obARotation[1][2] << " " << obARotation[2][0] << " " << obARotation[2][1] << " " <<  obARotation[2][2] << std::endl;
//        }
//        if (!obB->isStaticObject())
//        {
//            btMatrix3x3 obBRotation = obB->getWorldTransform().getBasis();
//            btVector3 obBPosition = obB->getWorldTransform().getOrigin();
//            motionsyncFile << ((bulletObject*)obB->getUserPointer())->id << " " << gSimulationTime << " " << obBPosition[0] << " " << obBPosition[1] << " " << obBPosition[2] << " " << obBRotation[0][0] << " " << obBRotation[0][1] << " " << obBRotation[0][2] << " " <<obBRotation[1][0] << " " << obBRotation[1][1] << " " << obBRotation[1][2] << " " << obBRotation[2][0] << " " << obBRotation[2][1] << " " <<  obBRotation[2][2] << std::endl;
//        }
        
        int numContacts = contactManifold->getNumContacts();
        for (int j = 0; j < numContacts; j++)
        {
            btManifoldPoint& pt = contactManifold->getContactPoint(j);

            // collision file output format
            // id time point.x point.y point.z normal.x normal.y normal.z impulse

            if (pt.getAppliedImpulse() > 0 && collisionFile.is_open()){
                std::cout << "Collision recorded at " << gSimulationTime << "s, between object " << ((bulletObject*)obA->getUserPointer())->id << " and object " << ((bulletObject*)obB->getUserPointer())->id << ". Impulse: " << pt.getAppliedImpulse() << std::endl;
                if (!obA->isStaticObject()){
                    collisionFile << ((bulletObject*)obA->getUserPointer())->id << " " << gSimulationTime << " " << pt.m_localPointA[0] << " " << pt.m_localPointA[1] << " " << pt.m_localPointA[2] << " " << -pt.m_normalWorldOnB[0] << " " << -pt.m_normalWorldOnB[1] << " " << -pt.m_normalWorldOnB[2] << " " << pt.getAppliedImpulse() << std::endl;
                }
                if (!obB->isStaticObject()){
                collisionFile << ((bulletObject*)obB->getUserPointer())->id << " " << gSimulationTime << " " << pt.m_localPointB[0] << " " << pt.m_localPointB[1] << " " << pt.m_localPointB[2] << " " << pt.m_normalWorldOnB[0] << " " << pt.m_normalWorldOnB[1] << " " << pt.m_normalWorldOnB[2] << " " << pt.getAppliedImpulse() << std::endl;
                }
            }
        }
    }
}

//void RigidBodyFromObjExample::initGImpactCollision(GLInstanceGraphicsShape* glmesh)
//{
//    btTriangleIndexVertexArray* indexVertexArray = new btTriangleIndexVertexArray(glmesh->m_numIndices, <#int *triangleIndexBase#>, 3*sizeof(int), glmesh->m_numvertices, <#btScalar *vertexBase#>, 3*sizeof(int));
//        btGImpactMeshShape* trimesh = new btGImpactMeshShape(indexVertexArray);
//}

struct inputObj {
    int id;
    std::string name;
    float mass;
    float collisionMargin;
    float orn[4];
    float pos[4];
    btVector3 linearVelocity;
    btVector3 angularVelocity;
    float friction;
    float restitution;
    float rollingFriction;
    float spinningFriction;
    float linearDamping;
    float angularDamping;
};

// bullet.input.dat format
// Line 1: number of objects N
// Line 2: id name mass collision_margin <quaternion(4)> <position(4)> <linear_velocity(3)> <angular_velocity(3)> friction restitution rolling_friction spinning_friction linear_damping angular_damping
// Line i: id name mass collision_margin <quaternion(4)> <position(4)> <linear_velocity(3)> <angular_velocity(3)> friction restitution rolling_friction spinning_friction linear_damping angular_damping
// Line N+1: id name mass collision_margin <quaternion(4)> <position(4)> <linear_velocity(3)> <angular_velocity(3)> friction restitution rolling_friction spinning_friction linear_damping angular_damping
// If name is "ground", then by default, it creats a groundshape with side of length 100, otherwise it import the mesh with input name. Note that ids should be unique.

void readObjectList (int &numObj, std::vector<inputObj> &objects)
{
    using namespace std;
    
    ifstream inputObjFile(objectList);
	if (!inputObjFile.is_open())
	{
		cout << "ERROR: cannot open object list file." << endl;
		return;
	}
    string str;
    getline(inputObjFile, str);
    numObj = stoi(str);
    while (getline(inputObjFile, str)) {
        istringstream iss(str);
        vector<std::string> tokens;
        copy(istream_iterator<string>(iss),
             istream_iterator<string>(),
             back_inserter(tokens));
        inputObj object;
        object.id = stoi(tokens[0]);
        object.name = tokens[1];
        object.mass = stof(tokens[2]);
        object.collisionMargin = stof(tokens[3]);
        object.orn[0] = stof(tokens[4]);
        object.orn[1] = stof(tokens[5]);
        object.orn[2] = stof(tokens[6]);
        object.orn[3] = stof(tokens[7]);
        object.pos[0] = stof(tokens[8]);
        object.pos[1] = stof(tokens[9]);
        object.pos[2] = stof(tokens[10]);
        object.pos[3] = stof(tokens[11]);
        object.linearVelocity = btVector3(stof(tokens[12]), stof(tokens[13]), stof(tokens[14]));
        object.angularVelocity = btVector3(stof(tokens[15]), stof(tokens[16]), stof(tokens[17]));
        object.friction = stof(tokens[18]);
        object.restitution = stof(tokens[19]);
        object.rollingFriction = stof(tokens[20]);
        object.spinningFriction = stof(tokens[21]);
        object.linearDamping = stof(tokens[22]);
        object.angularDamping = stof(tokens[23]);
        objects.push_back(object);
        
    }
    inputObjFile.close();
}


void RigidBodyFromObjExample::initPhysics()
{
	m_guiHelper->setUpAxis(1);

	createEmptyDynamicsWorld();
	
	m_guiHelper->createPhysicsDebugDrawer(m_dynamicsWorld);
    
    // Call back after solving the collision
    m_dynamicsWorld->setInternalTickCallback(callBack);

    int numObj;
    std::vector<inputObj> objects;
    readObjectList(numObj, objects);

    std::cout << "Number of objects is " << numObj << std::endl;
    
    for (int i = 0; i < numObj; i++)
    {
        if (objects[i].name == "ground"){
            std::cout << "No. " << i << "mesh created. Name " << objects[i].name << std::endl;
            ///create a few basic rigid bodies
            btBoxShape* groundShape = createBoxShape(btVector3(btScalar(50.),btScalar(50.),btScalar(50.)));
            m_collisionShapes.push_back(groundShape);
            

            btTransform groundTransform;
            groundTransform.setIdentity();
            groundTransform.setOrigin(btVector3(objects[i].pos[0],objects[i].pos[1],objects[i].pos[2]));
            {
                btScalar mass(0.);
                btRigidBody* body = createRigidBody(mass,groundTransform,groundShape, btVector4(0,0,1,1));
                
                //set collision flag and parameters
                body->setFriction(objects[i].friction);
                body->setRestitution(objects[i].restitution);
                body->setRollingFriction(objects[i].rollingFriction);
                body->setSpinningFriction(objects[i].spinningFriction);
                body->setDamping(objects[i].linearDamping, objects[i].angularDamping);

                body->setCollisionFlags(body->getCollisionFlags() | btCollisionObject::CF_CUSTOM_MATERIAL_CALLBACK);
                bodies.push_back(new bulletObject(body, objects[i].id));
                body->setUserPointer(bodies[bodies.size()-1]);
            }
            btMatrix3x3 objRotation = groundTransform.getBasis();
            btVector3 objPosition = groundTransform.getOrigin();
            std::cout << "At " << gSimulationTime << "s, object " << objects[i].id <<" origin position is [" << objPosition[0] << ", " << objPosition[1] << ", " << objPosition[2] << "]. " << "Rotation matrix: [[" << objRotation[0][0] << " " << objRotation[0][1] << " " << objRotation[0][2] << "] [" <<objRotation[1][0] << " " << objRotation[1][1] << " " << objRotation[1][2] << "] [" << objRotation[2][0] << " " <<  objRotation[2][1] << " " <<  objRotation[2][2] << "]]" << std::endl;
            motionFile << objects[i].id << " " << gSimulationTime << " " << objPosition[0] << " " << objPosition[1] << " " << objPosition[2] << " " << objRotation[0][0] << " " << objRotation[0][1] << " " << objRotation[0][2] << " " <<objRotation[1][0] << " " << objRotation[1][1] << " " << objRotation[1][2] << " " << objRotation[2][0] << " " <<  objRotation[2][1] << " " <<  objRotation[2][2] << std::endl;
        }
        // static concave mesh
	else if (std::stoi(objects[i].name) >= 1000){
            std::cout << "No. " << i << " mesh created. Name " << objects[i].name << std::endl;
            
            btTriangleIndexVertexArray* meshInterface = new btTriangleIndexVertexArray();
            btIndexedMesh part;
            
            std::string objName = objects[i].name + ".obj";
            const char* fileName = objName.c_str();
            char relativeFileName[1024];
            if (b3ResourcePath::findResourcePath(fileName, relativeFileName, 1024))
            {
                char pathPrefix[1024];
                b3FileUtils::extractPath(relativeFileName, pathPrefix, 1024);
            }
            
            GLInstanceGraphicsShape* glmesh = LoadMeshFromObj(relativeFileName, "");
            
            if (glmesh == nullptr) {
                std::cerr << "Cannot load mesh" << std::endl;
                exit(1);
            }
            
            printf("[INFO] Obj loaded: Extracted %d verticed from obj file [%s]\n", glmesh->m_numvertices, fileName);
            
            std::cout << "vertices num " << glmesh->m_numvertices << " indices num " << glmesh->m_numIndices << std::endl;
            
            btScalar *staticVtx = new btScalar[3*glmesh->m_numvertices];
            for (int i = 0; i < glmesh->m_numvertices; i++){
                staticVtx[3*i+0] = glmesh->m_vertices->at(i).xyzw[0];
                staticVtx[3*i+1] = glmesh->m_vertices->at(i).xyzw[1];
                staticVtx[3*i+2] = glmesh->m_vertices->at(i).xyzw[2];
//                std::cout << "v " << staticVtx[3*i] << ", " << staticVtx[3*i+1] << ", " << staticVtx[3*i+2] << std::endl;
            }
            
            int *staticIdx = new int[glmesh->m_numIndices];
            for (int i  = 0; i < glmesh->m_numIndices; i+=3){
                staticIdx[i] = glmesh->m_indices->at(i);
                staticIdx[i+1] = glmesh->m_indices->at(i+1);
                staticIdx[i+2] = glmesh->m_indices->at(i+2);
//                std::cout << "f " << staticIdx[i] << ", " << staticIdx[i+1] << ", " << staticIdx[i+2] << std::endl;

            }
            
            part.m_vertexBase = (const unsigned char*)staticVtx;
            part.m_vertexStride = sizeof(btScalar) * 3;
            part.m_numVertices = glmesh->m_numvertices;
            part.m_triangleIndexBase = (const unsigned char*)staticIdx;
            part.m_triangleIndexStride = sizeof(int) * 3;
            part.m_numTriangles = glmesh->m_numIndices/3;
            part.m_indexType = PHY_INTEGER;
            
            meshInterface->addIndexedMesh(part,PHY_INTEGER);
            
            bool	useQuantizedAabbCompression = true;
            btBvhTriangleMeshShape* trimeshShape = new btBvhTriangleMeshShape(meshInterface,useQuantizedAabbCompression);
            trimeshShape->setMargin(objects[i].collisionMargin);
            m_collisionShapes.push_back(trimeshShape);

            btVector3 localInertia(0,0,0);
            
            btTransform trans;
            trans.setIdentity();
            btVector3 position(objects[i].pos[0],objects[i].pos[1],objects[i].pos[2]);
            trans.setOrigin(position);
            btQuaternion quat(objects[i].orn[0], objects[i].orn[1], objects[i].orn[2], objects[i].orn[3]);
            
            btRigidBody* body = createRigidBody(0,trans,trimeshShape);
            body->setFriction(objects[i].friction);
            body->setRestitution(objects[i].restitution);
            body->setRollingFriction(objects[i].rollingFriction);
            body->setDamping(objects[i].linearDamping, objects[i].angularDamping);
            body->setCollisionFlags(body->getCollisionFlags() | btCollisionObject::CF_CUSTOM_MATERIAL_CALLBACK);
            bodies.push_back(new bulletObject(body, objects[i].id));
            body->setUserPointer(bodies[bodies.size()-1]);
            
            btMatrix3x3 objRotation = trans.getBasis();
            btVector3 objPosition = trans.getOrigin();
            std::cout << "At " << gSimulationTime << "s, object " << objects[i].id <<" origin position is [" << objPosition[0] << ", " << objPosition[1] << ", " << objPosition[2] << "]. " << "Rotation matrix: [[" << objRotation[0][0] << " " << objRotation[0][1] << " " << objRotation[0][2] << "] [" <<objRotation[1][0] << " " << objRotation[1][1] << " " << objRotation[1][2] << "] [" << objRotation[2][0] << " " <<  objRotation[2][1] << " " <<  objRotation[2][2] << "]]" << std::endl;
            motionFile << objects[i].id << " " << gSimulationTime << " " << objPosition[0] << " " << objPosition[1] << " " << objPosition[2] << " " << objRotation[0][0] << " " << objRotation[0][1] << " " << objRotation[0][2] << " " <<objRotation[1][0] << " " << objRotation[1][1] << " " << objRotation[1][2] << " " << objRotation[2][0] << " " <<  objRotation[2][1] << " " <<  objRotation[2][2] << std::endl;	
	}

        //load obj meshes
        else
        {
            //load our obj mesh
            std::cout << "No. " << i << "mesh created. Name " << objects[i].name << std::endl;
            std::string objName = objects[i].name + ".obj";
            const char* fileName = objName.c_str();
            char relativeFileName[1024];
            if (b3ResourcePath::findResourcePath(fileName, relativeFileName, 1024))
            {
                char pathPrefix[1024];
                b3FileUtils::extractPath(relativeFileName, pathPrefix, 1024);
            }

            GLInstanceGraphicsShape* glmesh = LoadMeshFromObj(relativeFileName, "");

			if (glmesh->m_numvertices == 0)
			{
				std::cout << "ERROR: invalid .obj file." << std::endl;
				return;
			}            

            printf("[INFO] Obj loaded: Extracted %d vertices from obj file [%s]\n", glmesh->m_numvertices, fileName);
            
            const GLInstanceVertex& v = glmesh->m_vertices->at(0);
            btConvexHullShape* shape = new btConvexHullShape((const btScalar*)(&(v.xyzw[0])), glmesh->m_numvertices, sizeof(GLInstanceVertex));
            
            float scaling[4] = {1,1,1,1};//{2.5,2.5,2.5,2.5};
            
            btVector3 localScaling(scaling[0],scaling[1],scaling[2]);
            shape->setLocalScaling(localScaling);
            
            if (m_options & OptimizeConvexObj)
            {
                shape->optimizeConvexHull();
            }
            
            if (m_options & ComputePolyhedralFeatures)
            {
                shape->initializePolyhedralFeatures();
            }
            
            
            shape->setMargin(objects[i].collisionMargin);
            m_collisionShapes.push_back(shape);
            
            btTransform startTransform;
            startTransform.setIdentity();
            btQuaternion quat = btQuaternion(objects[i].orn[0],objects[i].orn[1],objects[i].orn[2],objects[i].orn[3]);
	    startTransform.setRotation(quat); 
            btScalar	mass(objects[i].mass);
            bool isDynamic = (mass != 0.f);
            btVector3 localInertia(0,0,0);
            if (isDynamic)
                shape->calculateLocalInertia(mass,localInertia);
            
            float color[4] = {1,0,0,1};
            btVector3 position(objects[i].pos[0],objects[i].pos[1],objects[i].pos[2]);
            startTransform.setOrigin(position);
            btRigidBody* body = createRigidBody(mass,startTransform,shape);
            //set collision flag and parameters
            body->setLinearVelocity(objects[i].linearVelocity);
            body->setAngularVelocity(objects[i].angularVelocity);
            body->setFriction(objects[i].friction);
            body->setRestitution(objects[i].restitution);
            body->setRollingFriction(objects[i].rollingFriction);
            body->setSpinningFriction(objects[i].spinningFriction);
            body->setDamping(objects[i].linearDamping, objects[i].angularDamping);
            body->setCollisionFlags(body->getCollisionFlags() | btCollisionObject::CF_CUSTOM_MATERIAL_CALLBACK);
            bodies.push_back(new bulletObject(body, objects[i].id));
            body->setUserPointer(bodies[bodies.size()-1]);
            
            
            // motion output file format
            // id time position.x position.y position.z rotation.11 rotation12 rotation13 rotation21 rotation22 rotation23 rotation31 rotation32 rotation33
            
            btMatrix3x3 objRotation = startTransform.getBasis();
            btVector3 objPosition = startTransform.getOrigin();
            std::cout << "At " << gSimulationTime << "s, object " << objects[i].id <<" origin position is [" << objPosition[0] << ", " << objPosition[1] << ", " << objPosition[2] << "]. " << "Rotation matrix: [[" << objRotation[0][0] << " " << objRotation[0][1] << " " << objRotation[0][2] << "] [" <<objRotation[1][0] << " " << objRotation[1][1] << " " << objRotation[1][2] << "] [" << objRotation[2][0] << " " <<  objRotation[2][1] << " " <<  objRotation[2][2] << "]]" << std::endl;
            motionFile << objects[i].id << " " << gSimulationTime << " " << objPosition[0] << " " << objPosition[1] << " " << objPosition[2] << " " << objRotation[0][0] << " " << objRotation[0][1] << " " << objRotation[0][2] << " " <<objRotation[1][0] << " " << objRotation[1][1] << " " << objRotation[1][2] << " " << objRotation[2][0] << " " <<  objRotation[2][1] << " " <<  objRotation[2][2] << std::endl;
            
            
            bool useConvexHullForRendering = ((m_options & ObjUseConvexHullForRendering)!=0);
            
            
            if (!useConvexHullForRendering)
            {
                int shapeId = m_guiHelper->registerGraphicsShape(&glmesh->m_vertices->at(0).xyzw[0], 
                                                                 glmesh->m_numvertices, 
                                                                 &glmesh->m_indices->at(0), 
                                                                 glmesh->m_numIndices,
                                                                 B3_GL_TRIANGLES, -1);
                shape->setUserIndex(shapeId);
                int renderInstance = m_guiHelper->registerGraphicsInstance(shapeId,objects[i].pos,objects[i].orn,color,scaling);
                body->setUserIndex(renderInstance);
            }
        }
    }
    objects.clear();
	m_guiHelper->autogenerateGraphicsObjects(m_dynamicsWorld);
    
}

void RigidBodyFromObjExample::exitPhysics()
{
    for (int i = 0; i < bodies.size(); i++)
    {
        m_dynamicsWorld->removeCollisionObject(bodies[i]->body);
        btMotionState* motionState=bodies[i]->body->getMotionState();
        btCollisionShape* shape=bodies[i]->body->getCollisionShape();
        delete bodies[i]->body;
        delete shape;
        delete motionState;
        delete bodies[i];
    }
    bodies.clear();
    delete m_dispatcher;
    delete m_collisionConfiguration;
    delete m_solver;
    delete m_broadphase;
    delete m_dynamicsWorld;

}

void RigidBodyFromObjExample::renderScene()
{
	CommonRigidBodyBase::renderScene();
}



CommonExampleInterface*    ET_RigidBodyFromObjCreateFunc(CommonExampleOptions& options)
{
//    gContactAddedCallback = callbackFunc;
	return new RigidBodyFromObjExample(options.m_guiHelper,options.m_option);
}

B3_STANDALONE_EXAMPLE(ET_RigidBodyFromObjCreateFunc)

