/*
Bullet Continuous Collision Detection and Physics Library
Copyright (c) 2015 Google Inc. http://bulletphysics.org

This software is provided 'as-is', without any express or implied warranty.
In no event will the authors be held liable for any damages arising from the use of this software.
Permission is granted to anyone to use this software for any purpose, 
including commercial applications, and to alter it and redistribute it freely, 
subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment in the product documentation would be appreciated but is not required.
2. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
3. This notice may not be removed or altered from any source distribution.
*/

#include <iostream>
#include <fstream>

#include "../CommonInterfaces/CommonExampleInterface.h"
#include "../CommonInterfaces/CommonGUIHelperInterface.h"
#include "../Utils/b3Clock.h"

#include "../OpenGLWindow/SimpleOpenGL3App.h"
#include <stdio.h>
#include "../ExampleBrowser/OpenGLGuiHelper.h"
#include <vector>


extern double  gSimulationTime;
extern float dist, pitch, yaw, targetPos0, targetPos1, targetPos2;
extern char* objectList;

CommonExampleInterface*    example;
int gSharedMemoryKey=-1;

b3MouseMoveCallback prevMouseMoveCallback = 0;
static void OnMouseMove( float x, float y)
{
	bool handled = false; 
	handled = example->mouseMoveCallback(x,y); 	 
	if (!handled)
	{
		if (prevMouseMoveCallback)
			prevMouseMoveCallback (x,y);
	}
}

b3MouseButtonCallback prevMouseButtonCallback  = 0;
static void OnMouseDown(int button, int state, float x, float y) {
	bool handled = false;

	handled = example->mouseButtonCallback(button, state, x,y); 
	if (!handled)
	{
		if (prevMouseButtonCallback )
			prevMouseButtonCallback (button,state,x,y);
	}
}

class LessDummyGuiHelper : public DummyGUIHelper
{
	CommonGraphicsApp* m_app;
public:
	virtual CommonGraphicsApp* getAppInterface()
	{
		return m_app;
	}

	LessDummyGuiHelper(CommonGraphicsApp* app)
		:m_app(app)
	{
	}
};
int main(int argc, char* argv[])
{
	if (argc != 3) 
	{
		std::cerr << "Usage: " << argv[0] << " <bullet.cfg> <bullet.input.dat>" << std::endl;
		return 1;
	}
    const char* cfgFile = argv[1];
	objectList = argv[2];
    static std::ifstream config (cfgFile);
    if (!config.is_open())
	{
		std::cout << "ERROR: cannot open config file." << std::endl;
		return 1;
	}
	std::string str;
    std::getline(config, str);
    bool GUI = std::stoi(str);          // 1st Line: GUI
    std::getline(config, str);
    int fps = std::stoi(str);           // 2nd Line: fps
    std::getline(config, str);
    float duration = std::stof(str);    // 3rd Line: duration
    std::getline(config, str);
    dist = std::stof(str);        // 4th Line: camera distance
    std::getline(config, str);
    pitch = std::stof(str);       // 5th Line: camera pitch
    std::getline(config, str);
    yaw = std::stof(str);         // 6th Line: camera yaw
//    float targetPos[3];
    std::getline(config, str);
    targetPos0 = std::stof(str);      // 7th Line: target position.x
    std::getline(config, str);
    targetPos1 = std::stof(str);      // 8th Line: target position.y
    std::getline(config, str);
    targetPos2 = std::stof(str);      // 9th Line: target position.z
    config.close();
    
    if (GUI) {
        SimpleOpenGL3App* app = new SimpleOpenGL3App("Bullet Standalone Example",1024,768,true);
        
        prevMouseButtonCallback = app->m_window->getMouseButtonCallback();
        prevMouseMoveCallback = app->m_window->getMouseMoveCallback();

        app->m_window->setMouseButtonCallback((b3MouseButtonCallback)OnMouseDown);
        app->m_window->setMouseMoveCallback((b3MouseMoveCallback)OnMouseMove);
        
        OpenGLGuiHelper gui(app,false);
        //LessDummyGuiHelper gui(app);
        //DummyGUIHelper gui;

        CommonExampleOptions options(&gui);
        

        example = StandaloneExampleCreateFunc(options);
        example->processCommandLineArgs(argc, argv);

        example->initPhysics();

        example->resetCamera();
        
        
        b3Clock clock;

        double timeStep = 1.0/fps;
        for (double time = timeStep; time < duration; time += timeStep) {
            app->m_instancingRenderer->init();
            app->m_instancingRenderer->updateCamera(app->getUpAxis());
            
            gSimulationTime += timeStep;
            
            example->stepSimulation(timeStep);
            
            example->renderScene();
            
            DrawGridData dg;
            dg.upAxis = app->getUpAxis();
            app->drawGrid(dg);
            
            app->swapBuffer();
        }
        
        example->exitPhysics();
        delete example;
        delete app;
    }
    
    else {
        DummyGUIHelper gui;
        
        CommonExampleOptions options(& gui);
        example = StandaloneExampleCreateFunc(options);
        example->processCommandLineArgs(argc, argv);
        
        example->initPhysics();
        
        example->resetCamera();
        
        double timeStep = 1.0/fps;
        for (double time = timeStep; time < duration; time += timeStep) {
            gSimulationTime += timeStep;
            example->stepSimulation(timeStep);
        }

        example->exitPhysics();
        delete example;
    }
    
    return 0;
    
//	do
//	{
//		app->m_instancingRenderer->init();
//    app->m_instancingRenderer->updateCamera(app->getUpAxis());
//
//		btScalar dtSec = btScalar(clock.getTimeInSeconds());
////		if (dtSec<0.1)
////			dtSec = 0.1;
//        
////        const int DIVISOR = 3;
////        
////        for (int i = 0; i < DIVISOR; i++) {
////            gSimulationTime += dtSec / DIVISOR;
////            example->stepSimulation(dtSec / DIVISOR);
////        }
//        gSimulationTime += dtSec;
//        example->stepSimulation(dtSec);
//        
//	  clock.reset();
//
//		example->renderScene();
// 	
//		DrawGridData dg;
//        dg.upAxis = app->getUpAxis();
//		app->drawGrid(dg);
//		
//		app->swapBuffer();
//	} while (!app->m_window->requestedExit());
//
//	example->exitPhysics();
//	delete example;
//	delete app;
//	return 0;
}

