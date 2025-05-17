\
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "structmember.h" // For PyMemberDef
#include "game_loop.h"    // Your original C game loop header

// Forward declaration of C callback adapter functions
static void process_input_c_adapter(void* user_data);
static void update_c_adapter(double dt, void* user_data);
static void render_c_adapter(double alpha, void* user_data);

// Define the Python GameLoop object structure
typedef struct {
    PyObject_HEAD
    GameLoop loop_instance;       // Instance of your C GameLoop
    PyObject *process_input_cb; // Python callback for process_input
    PyObject *update_cb;        // Python callback for update
    PyObject *render_cb;        // Python callback for render
} PyGameLoopObject;

// Deallocator for PyGameLoopObject
static void PyGameLoop_dealloc(PyGameLoopObject *self) {
    Py_XDECREF(self->process_input_cb);
    Py_XDECREF(self->update_cb);
    Py_XDECREF(self->render_cb);
    // If GameLoop_init allocated any resources that GameLoop_stop doesn't clean,
    // clean them here. For now, assuming GameLoop_stop is sufficient or no extra allocs.
    if (self->loop_instance.is_running) {
        GameLoop_stop(&self->loop_instance);
    }
    Py_TYPE(self)->tp_free((PyObject *) self);
}

// __new__ method (usually not needed if tp_init is well-defined)
static PyObject *PyGameLoop_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    PyGameLoopObject *self;
    self = (PyGameLoopObject *) type->tp_alloc(type, 0);
    if (self != NULL) {
        self->process_input_cb = Py_None; Py_INCREF(Py_None);
        self->update_cb = Py_None; Py_INCREF(Py_None);
        self->render_cb = Py_None; Py_INCREF(Py_None);
        // Initialize loop_instance with default values or leave to __init__
    }
    return (PyObject *) self;
}

// __init__ method for PyGameLoopObject
static int PyGameLoop_init(PyGameLoopObject *self, PyObject *args, PyObject *kwds) {
    double fixed_time_step = 1.0 / 60.0;
    static char *kwlist[] = {"fixed_time_step", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|d", kwlist, &fixed_time_step)) {
        return -1;
    }

    GameLoop_init(&self->loop_instance, fixed_time_step);
    // Pass 'self' as user_data to C callbacks so they can find the Python object
    GameLoop_set_user_data(&self->loop_instance, self); 
    return 0;
}

// Method to start the game loop
static PyObject *PyGameLoop_start(PyGameLoopObject *self, PyObject *Py_UNUSED(ignored)) {
    if (!self->loop_instance.is_running) {
        // Before starting the loop, ensure C callbacks are set if Python callbacks exist
        if (self->process_input_cb != Py_None && PyCallable_Check(self->process_input_cb)) {
            GameLoop_set_process_input_handler_with_user_data(&self->loop_instance, process_input_c_adapter);
        } else {
            GameLoop_set_process_input_handler_with_user_data(&self->loop_instance, NULL);
        }
        if (self->update_cb != Py_None && PyCallable_Check(self->update_cb)) {
            GameLoop_set_update_handler_with_user_data(&self->loop_instance, update_c_adapter);
        } else {
            GameLoop_set_update_handler_with_user_data(&self->loop_instance, NULL);
        }
        if (self->render_cb != Py_None && PyCallable_Check(self->render_cb)) {
            GameLoop_set_render_handler_with_user_data(&self->loop_instance, render_c_adapter);
        } else {
            GameLoop_set_render_handler_with_user_data(&self->loop_instance, NULL);
        }

        // Release the GIL while the C game loop runs
        Py_BEGIN_ALLOW_THREADS
        GameLoop_start(&self->loop_instance);
        Py_END_ALLOW_THREADS
    }
    Py_RETURN_NONE;
}

// Method to stop the game loop
static PyObject *PyGameLoop_stop(PyGameLoopObject *self, PyObject *Py_UNUSED(ignored)) {
    GameLoop_stop(&self->loop_instance);
    Py_RETURN_NONE;
}

// Helper to set callback
static PyObject *set_callback(PyGameLoopObject *self, PyObject *arg, PyObject **target_cb_ptr) {
    PyObject *tmp;
    if (arg == Py_None) { // Allow unsetting with None
        tmp = *target_cb_ptr;
        Py_INCREF(Py_None);
        *target_cb_ptr = Py_None;
        Py_XDECREF(tmp);
        Py_RETURN_NONE;
    }
    if (!PyCallable_Check(arg)) {
        PyErr_SetString(PyExc_TypeError, "Parameter must be a callable");
        return NULL;
    }
    tmp = *target_cb_ptr;
    Py_INCREF(arg);
    *target_cb_ptr = arg;
    Py_XDECREF(tmp);
    Py_RETURN_NONE;
}

// Method to set the process_input handler
static PyObject *PyGameLoop_set_process_input_handler(PyGameLoopObject *self, PyObject *args) {
    PyObject *callback = NULL;
    if (!PyArg_ParseTuple(args, "O", &callback)) return NULL;
    PyObject* result = set_callback(self, callback, &self->process_input_cb);
    if (result != NULL && self->process_input_cb != Py_None) {
         GameLoop_set_process_input_handler_with_user_data(&self->loop_instance, process_input_c_adapter);
    } else if (result != NULL) {
         GameLoop_set_process_input_handler_with_user_data(&self->loop_instance, NULL);
    }
    return result;
}

// Method to set the update handler
static PyObject *PyGameLoop_set_update_handler(PyGameLoopObject *self, PyObject *args) {
    PyObject *callback = NULL;
    if (!PyArg_ParseTuple(args, "O", &callback)) return NULL;
    PyObject* result = set_callback(self, callback, &self->update_cb);
     if (result != NULL && self->update_cb != Py_None) {
         GameLoop_set_update_handler_with_user_data(&self->loop_instance, update_c_adapter);
    } else if (result != NULL) {
         GameLoop_set_update_handler_with_user_data(&self->loop_instance, NULL);
    }
    return result;
}

// Method to set the render handler
static PyObject *PyGameLoop_set_render_handler(PyGameLoopObject *self, PyObject *args) {
    PyObject *callback = NULL;
    if (!PyArg_ParseTuple(args, "O", &callback)) return NULL;
    PyObject* result = set_callback(self, callback, &self->render_cb);
    if (result != NULL && self->render_cb != Py_None) {
         GameLoop_set_render_handler_with_user_data(&self->loop_instance, render_c_adapter);
    } else if (result != NULL) {
         GameLoop_set_render_handler_with_user_data(&self->loop_instance, NULL);
    }
    return result;
}

// Getter for is_running property
static PyObject *PyGameLoop_get_is_running(PyGameLoopObject *self, void *closure) {
    if (GameLoop_is_running(&self->loop_instance)) {
        Py_RETURN_TRUE;
    }
    Py_RETURN_FALSE;
}

// C adapter for process_input callback
static void process_input_c_adapter(void* user_data) {
    PyGameLoopObject *self = (PyGameLoopObject*)user_data;
    if (self && self->process_input_cb != Py_None && PyCallable_Check(self->process_input_cb)) {
        PyGILState_STATE gstate = PyGILState_Ensure();
        PyObject *result = PyObject_CallObject(self->process_input_cb, NULL);
        if (result == NULL) {
            // An exception occurred in the Python callback.
            // You might want to stop the loop or handle it.
            // For now, just print it.
            PyErr_Print();
            // Optionally stop the loop:
            // GameLoop_stop(&self->loop_instance);
        }
        Py_XDECREF(result);
        PyGILState_Release(gstate);
    }
}

// C adapter for update callback
static void update_c_adapter(double dt, void* user_data) {
    PyGameLoopObject *self = (PyGameLoopObject*)user_data;
    if (self && self->update_cb != Py_None && PyCallable_Check(self->update_cb)) {
        PyGILState_STATE gstate = PyGILState_Ensure();
        PyObject *arg = PyFloat_FromDouble(dt);
        PyObject *result = PyObject_CallFunctionObjArgs(self->update_cb, arg, NULL);
        Py_XDECREF(arg);
        if (result == NULL) {
            PyErr_Print();
            // Optionally stop the loop:
            // GameLoop_stop(&self->loop_instance);
        }
        Py_XDECREF(result);
        PyGILState_Release(gstate);
    }
}

// C adapter for render callback
static void render_c_adapter(double alpha, void* user_data) {
    PyGameLoopObject *self = (PyGameLoopObject*)user_data;
    if (self && self->render_cb != Py_None && PyCallable_Check(self->render_cb)) {
        PyGILState_STATE gstate = PyGILState_Ensure();
        PyObject *arg = PyFloat_FromDouble(alpha);
        PyObject *result = PyObject_CallFunctionObjArgs(self->render_cb, arg, NULL);
        Py_XDECREF(arg);
        if (result == NULL) {
            PyErr_Print();
            // Optionally stop the loop:
            // GameLoop_stop(&self->loop_instance);
        }
        Py_XDECREF(result);
        PyGILState_Release(gstate);
    }
}


// Method definition table for PyGameLoopObject
static PyMethodDef PyGameLoop_methods[] = {
    {"start", (PyCFunction) PyGameLoop_start, METH_NOARGS, "Starts the game loop."},
    {"stop", (PyCFunction) PyGameLoop_stop, METH_NOARGS, "Stops the game loop."},
    {"set_process_input_handler", (PyCFunction) PyGameLoop_set_process_input_handler, METH_VARARGS, "Sets the handler for processing input."},
    {"set_update_handler", (PyCFunction) PyGameLoop_set_update_handler, METH_VARARGS, "Sets the handler for updating game state."},
    {"set_render_handler", (PyCFunction) PyGameLoop_set_render_handler, METH_VARARGS, "Sets the handler for rendering the game."},
    {NULL}  /* Sentinel */
};

// Property definition for is_running
static PyGetSetDef PyGameLoop_getsetters[] = {
    {"is_running", (getter) PyGameLoop_get_is_running, NULL, "True if the game loop is running", NULL},
    {NULL}  /* Sentinel */
};

// Type definition for PyGameLoopObject
static PyTypeObject PyGameLoopType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "gameloop_ext.GameLoop",
    .tp_doc = "GameLoop object implemented in C",
    .tp_basicsize = sizeof(PyGameLoopObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = PyGameLoop_new,
    .tp_init = (initproc) PyGameLoop_init,
    .tp_dealloc = (destructor) PyGameLoop_dealloc,
    .tp_methods = PyGameLoop_methods,
    .tp_getset = PyGameLoop_getsetters,
};

// Module definition
static PyModuleDef gameloop_ext_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "gameloop_ext",
    .m_doc = "A C extension module for the GameLoop pattern.",
    .m_size = -1,
};

// Module initialization function
PyMODINIT_FUNC PyInit_gameloop_ext(void) {
    PyObject *m;
    if (PyType_Ready(&PyGameLoopType) < 0)
        return NULL;

    m = PyModule_Create(&gameloop_ext_module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&PyGameLoopType);
    if (PyModule_AddObject(m, "GameLoop", (PyObject *) &PyGameLoopType) < 0) {
        Py_DECREF(&PyGameLoopType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
