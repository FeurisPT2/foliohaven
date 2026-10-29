cmake_minimum_required(VERSION 3.20)
project(FolioHaven VERSION 1.0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_PREFIX_PATH "C:/Qt/6.6.3/mingw_64")

find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets Sql Svg)
qt_standard_project_setup()

set(SOURCES
    src/storage/DatabaseManager.h
    src/storage/DatabaseManager.cpp
    src/engine/DocumentEngine.h
    src/engine/DocumentEngine.cpp
    src/ui/ReaderWindow.h
    src/ui/ReaderWindow.cpp
    src/app/main.cpp
)

add_executable(FolioHaven WIN32 ${SOURCES})

target_link_libraries(FolioHaven PRIVATE
    Qt6::Core
    Qt6::Gui
    Qt6::Widgets
    Qt6::Sql
    Qt6::Svg
    ole32
    oleaut32
)
