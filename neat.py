import numpy as np
import math
import copy
import random
import imageio
import sys
import os

# o0 = path = os.path.abspath("0")
# o1 = path = os.path.abspath("1")

# database = []

# for img in os.listdir(o0):
    # loc = os.path.join(o0,img)
    # img_fp = imageio.imread(loc)
    # img_fp.reshape((1,img_fp.size))
    # database.append((img_fp,0))
    
# for img in os.listdir(o1):
    # loc = os.path.join(o1,img)
    # img_fp = imageio.imread(loc)
    # img_fp.reshape((1,img_fp.size))
    # database.append((img_fp,1))
    

# Hyperparameters
MAX_EDGE = 10
PARENTS = 2
POPULATION = 1000
SURVIVORS = round(math.sqrt(POPULATION))
MUTATION_RATE = 50
BRANCH_FACTOR = SURVIVORS
JUMP = 0.1

#define more activation functions - softmax? swish? non linear cube?

def relu(x):
    return x * (x > 0)

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

ACTIVATION_FUNCTIONS = [relu, sigmoid]

class Layer():
    def __init__(self, n_nodes, input_size): #input will be nx1 array representing the node values of the previous layer, output will be layer * input
        self.input_size = input_size
        self.output_size = n_nodes
        self.edges = np.asmatrix(np.random.random_sample((n_nodes,input_size)))

class Mind():
    # add a population of layers which makes the input size the same as the nodes in the last layer
    def __init__(self, input_size, activation):
        self.hidden_layers = [Layer(input_size+1, input_size+1), Layer(1, input_size+1)]
        self.input_size = input_size+1
        self.fitness = 0
        self.activation = activation

    def prediction(self, input_v):
        # reshape 1xn input vector as nx1
        input_v = np.asmatrix(np.reshape(input_v,(np.array(input_v).size,1)))
        
        for layer in self.hidden_layers:
            intermediate = layer.edges * input_v
            # apply activation function
            for (index,elem) in enumerate(intermediate):
                intermediate[index] = ACTIVATION_FUNCTIONS[self.activation](elem)
            input_v = intermediate
        #return round(float(input_v)) for output if classification task
        return (float(input_v))
    
    def addLayer(self): # will add a layer at the end of the network
        input_size = self.hidden_layers[-2].output_size
        output_size = self.hidden_layers[-1].input_size
        l = Layer(output_size, input_size)
        self.hidden_layers.insert(-1,l)
    
    # currently only changes the weights, to add in changing layers later
    def mutate(self):
        replica = copy.deepcopy(self)
        
        for layer in replica.hidden_layers:
            for index in range(len(layer.edges)):
                roll = random.randint(0,100)
                if roll <= MUTATION_RATE:
                    current = layer.edges[index]
                    layer.edges[index] = random.uniform(current - JUMP,current + JUMP)
        roll = random.randint(0,100)
        if roll <= MUTATION_RATE:
            replica.addLayer()
        
        return replica
        
# use pickle library for data persistence
class Population():
    def __init__(self, input_size, activation):
        self.minds = [Mind(input_size, activation) for _ in range(POPULATION)]
        self.input_size = input_size
        self.activation = activation
    
    def prediction(self, input_v):
        return self.minds[0].prediction(input_v + [1])
    
    def determine_fitness(self,data):
        for mind in self.minds:
            error = 0
            count = 0
            for (vector, output) in data:
                error += (mind.prediction(vector+[1]) - output) ** 2
                count += 1
            # using mean squared error
            mind.fitness = error/count
    
    def next_gen(self, data):
        self.determine_fitness(data)
        self.minds.sort(key=lambda x: x.fitness)
        survivors = self.minds[:SURVIVORS]
        next_gen = []
        for genotype in survivors:
            for _ in range(BRANCH_FACTOR):
                next_gen.append(genotype.mutate())
        self.minds = survivors + next_gen + [Mind(self.input_size, self.activation) for _ in range(BRANCH_FACTOR)]

    def train(self, data):
        self.next_gen(data)
        while self.minds[0].fitness >= 0.01:
            print(self.minds[0].fitness)
            self.next_gen(data)
    
#define combination function with list of parents
#Select each layer from a probability distribution determined by relative fitness of parents, with a chance to delete or add layer
#Each layer selected will have weights drawn randomly from a parent (including the activation function for that node), chance to change weight, chance to change activation function


# define population as having a number of minds of a particular activation function

# debugging dataset
dataset = [([0,0],0),([0,1],1),([1,0],1),([1,1],0)]
a = Population(2,0)
