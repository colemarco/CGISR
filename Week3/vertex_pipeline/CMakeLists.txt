cmake_minimum_required(VERSION 3.10)
project(vertex_transformation_pipeline)

set(CMAKE_CXX_STANDARD 17)

# Find required packages
find_package(glfw3 REQUIRED)
find_package(OpenGL REQUIRED)

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/include)

# Add glad source
set(GLAD_SRC ${CMAKE_SOURCE_DIR}/src/glad.c)

# Add executable
add_executable(${PROJECT_NAME} main.cpp ${GLAD_SRC})

# Link libraries
target_link_libraries(${PROJECT_NAME} glfw OpenGL::GL)