# %%
import copy
import itertools

# %%
#############   Category Class   ###############

# src: morphism names --> object names
# target: morphism names --> object names
# comp: (morphism, morphism) --> morphism
# identityMap: objects --> morphisms

class Category:
    def __init__(self, 
                 src:dict, 
                 target:dict, 
                 comp:dict, 
                 identityMap:dict = {}, 
                 debug:bool = False) -> None:
        self.src = src
        self.target = target
        self.comp = comp
        self.objects = set(src.values()).union(set(target.values()))
        self.morphisms = list(src.keys())
        self.identityMap = identityMap
        self.debug = debug

        # if no identities are given add identities
        if identityMap == {}:
            self.addIdentities()

        # verify essential properties
        assert set(identityMap.keys()) == self.objects
        assert self.src.keys() == self.target.keys()
        assert self.composabilityCheck()
        assert self.compositionCheck()
        assert self.associativityCheck()
        
    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        return str((self.src, self.target, self.comp))

    # given identityMap, fill out missing data in src, target, comp
    def completeIdentities(self) -> None:
        for thisObject in self.objects:
            thisMorphism = self.identityMap[thisObject]
            self.src[thisMorphism] = thisObject
            self.target[thisMorphism] = thisObject
            if thisMorphism not in self.morphisms:
                self.morphisms = self.morphisms + [thisMorphism]
            self.identityMap[thisObject] = thisMorphism
            for i in self.morphisms:
                if self.src[i] == thisObject:
                    self.comp[(i, thisMorphism)] = i
                if self.target[i] == thisObject:
                    self.comp[(thisMorphism, i)] = i

    # Check that all the composables have matching targets and sources.
    def composabilityCheck(self)-> bool:
        for second,first in self.comp.keys():
            if self.target[first] != self.src[second]:
                if self.debug:
                    print("Composability violation...")
                return False
        return True
    
    # Check that any two composable morphisms have a name
    def compositionCheck(self) -> bool:
        for first in self.morphisms:
            for second in self.morphisms:
                if self.src[second] == self.target[first]:
                    if (second, first) not in self.comp.keys():
                        if self.debug:
                            print("Composables lack a name: ")
                            print("second, first: %s %s" % (second,first))
                        return False
        return True
    
    # Check associativity
    def associativityCheck(self) -> bool:
        for first in self.morphisms:
            for second in self.morphisms:
                for third in self.morphisms:
                    if (self.src[third] == self.target[second]) and (self.src[second] == self.target[first]):
                        if self.comp[(third, self.comp[second, first])] != self.comp[(self.comp[third, second], first)]:
                            if self.debug:
                                print("Associativty failure...")
                            return False
        return True
    
    # add identity morphisms to set of morphisms
    def addIdentities(self) -> None:
        for thisObject in self.objects:
            thisMorphism = "id_" + str(thisObject)
            self.identityMap[thisObject] = thisMorphism
        self.completeIdentities()


#############   Functor Class   ###################

# srcCat: Category
# targetCat: Category
# objectMap: objects --> objects
# morphismMap: morphisms --> morphisms

class Functor:
    def __init__(self, 
                 srcCat: Category, 
                 targetCat: Category, 
                 objectMap: dict, 
                 morphismMap: dict, 
                 debug: bool = False) -> None:
        self.srcCat = srcCat
        self.targetCat = targetCat
        self.objectMap = objectMap
        self.morphismMap = morphismMap
        self.debug = debug

        assert self.identityCheck()
        assert self.homomorphismFunctorCheck()

    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        #return str((self.srcCat, self.targetCat, self.objectMap, self.morphismMap))
        return str(self.objectMap) + '\n' + str(self.morphismMap) + '\n'
    
    # verify identity morphisms are mapped correctly
    def identityCheck(self) -> bool:
        for ob,thisID in self.srcCat.identityMap.items():
            if self.morphismMap[thisID] != self.targetCat.identityMap[self.objectMap[ob]]:
                if self.debug:
                    print("Functor does not preserve identities...")
                return False
        return True

    # verify composition is preserved
    def homomorphismFunctorCheck(self) -> bool:
        for first in self.srcCat.morphisms:

            # check that objects and morphisms are mapped consistently
            srcViolation = self.objectMap[self.srcCat.src[first]] != self.targetCat.src[self.morphismMap[first]]
            targetViolation = self.objectMap[self.srcCat.target[first]] != self.targetCat.target[self.morphismMap[first]]
            if srcViolation or targetViolation:
                if self.debug:
                    print("Functor violation...")
                return False
            
            # check that composition is preserved
            for second in self.srcCat.morphisms:
                if self.srcCat.src[second] == self.srcCat.target[first]:
                    srcComp = self.srcCat.comp[(second,first)]
                    targetComp = self.targetCat.comp[(self.morphismMap[second], self.morphismMap[first])]
                    if self.morphismMap[srcComp] != targetComp:
                        if self.debug:
                            print("Functor composition violation...")
                        return False
        return True


##############  Strict 2-Category Class   ##################

# zeroCells: list
# hom: (zeroCell, zeroCell) --> Category
# identityMap: zeroCell --> oneCell (in the category hom(A,A))
# comp: (A: zeroCell, B: zeroCell, C: zeroCell) ---> functor ( Hom(B,C)) x Hom(A, B) --> Hom(A, C) )

class StrictTwoCategory:
    def __init__(self, zeroCells:list, hom:dict, identityMap:dict, comp:dict) -> None:
        self.zeroCells = zeroCells
        self.hom = hom
        self.identityMap = identityMap
        self.comp = comp

        # verify essential properties
        assert self.identityOneCell()
        assert self.identityTwoCell()
        assert self.associativityOneCell()
        assert self.associativityTwoCell()
        
    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        return str((self.zeroCells, self.hom, self.identityMap, self.comp))
    
    # check that identities work for one cells
    def identityOneCell(self) -> bool:
        for thisZeroCell in self.zeroCells:
            thisIdentityOneCell = self.identityMap[thisZeroCell]
            for zeroCell in self.zeroCells:

                # identity morphism is second
                if (zeroCell,thisZeroCell) in self.hom.keys():
                    thisCompositionFunctor = self.comp[(zeroCell, thisZeroCell, thisZeroCell)]
                    thisOneCellMap = thisCompositionFunctor.objectMap
                    for thisOneCell in self.hom[(zeroCell, thisZeroCell)].objects:
                        if thisOneCellMap[(thisIdentityOneCell, thisOneCell)] != thisOneCell:
                            return False
                        
                # identity morphism is first
                if (thisZeroCell, zeroCell) in self.hom.keys():
                    thisCompositionFunctor = self.comp[(thisZeroCell, thisZeroCell, zeroCell)]
                    thisOneCellMap = thisCompositionFunctor.objectMap
                    for thisOneCell in self.hom[(thisZeroCell, zeroCell)].objects:
                        if thisOneCellMap[(thisOneCell, thisIdentityOneCell)] != thisOneCell:
                            return False
                        
        return True
    
    # check that identities work for two cells
    def identityTwoCell(self) -> bool:
        for thisZeroCell in self.zeroCells:
            thisCategory = self.hom[(thisZeroCell, thisZeroCell)]
            thisIdentityOneCell = self.identityMap[thisZeroCell]
            thisIdentityTwoCell = thisCategory.identityMap[thisIdentityOneCell]

            for zeroCell in self.zeroCells:

                # identity morphism is second
                if (zeroCell,thisZeroCell) in self.hom.keys():
                    thisCompositionFunctor = self.comp[(zeroCell, thisZeroCell, thisZeroCell)]
                    thisTwoCellMap = thisCompositionFunctor.morphismMap
                    for thisTwoCell in self.hom[(zeroCell, thisZeroCell)].morphisms:
                        if thisTwoCellMap[(thisIdentityTwoCell, thisTwoCell)] != thisTwoCell:
                            return False
                        
                # identity morphism is first
                if (thisZeroCell, zeroCell) in self.hom.keys():
                    thisCompositionFunctor = self.comp[(thisZeroCell, thisZeroCell, zeroCell)]
                    thisTwoCellMap = thisCompositionFunctor.morphismMap
                    for thisTwoCell in self.hom[(thisZeroCell, zeroCell)].morphisms:
                        if thisTwoCellMap[(thisTwoCell, thisIdentityTwoCell)] != thisTwoCell:
                            return False
        
        return True
    
    # verify one cell composition is associative
    def associativityOneCell(self) -> bool:
        for aZeroCell in self.zeroCells:
            for bZeroCell in self.zeroCells:
                for cZeroCell in self.zeroCells:
                    for dZeroCell in self.zeroCells:
                        if (aZeroCell, bZeroCell) in self.hom.keys() and (bZeroCell, cZeroCell) in self.hom.keys() and (cZeroCell, dZeroCell) in self.hom.keys():
                            for abOneCell in self.hom[(aZeroCell, bZeroCell)].objects:
                                for bcOneCell in self.hom[(bZeroCell, cZeroCell)].objects:
                                    for cdOneCell in self.hom[(cZeroCell, dZeroCell)].objects:
                                        abcCompositionFunctor = self.comp[(aZeroCell, bZeroCell, cZeroCell)]
                                        bcdCompositionFunctor = self.comp[(bZeroCell, cZeroCell, dZeroCell)]
                                        abcOneCellMap = abcCompositionFunctor.objectMap
                                        bcdOneCellMap = bcdCompositionFunctor.objectMap
                                        abcFirst = bcdOneCellMap[(cdOneCell, abcOneCellMap[(bcOneCell, abOneCell)])]
                                        bcdFirst = abcOneCellMap[(bcdOneCellMap[(cdOneCell, bcOneCell)], abOneCell)]
                                        if abcFirst != bcdFirst:
                                            return False
                                        
        return True
    
    # verify two cell composition is associative
    def associativityTwoCell(self) -> bool:
        for aZeroCell in self.zeroCells:
            for bZeroCell in self.zeroCells:
                for cZeroCell in self.zeroCells:
                    for dZeroCell in self.zeroCells:
                        if (aZeroCell, bZeroCell) in self.hom.keys() and (bZeroCell, cZeroCell) in self.hom.keys() and (cZeroCell, dZeroCell) in self.hom.keys():
                            for abTwoCell in self.hom[(aZeroCell, bZeroCell)].morphisms:
                                for bcTwoCell in self.hom[(bZeroCell, cZeroCell)].morphisms:
                                    for cdTwoCell in self.hom[(cZeroCell, dZeroCell)].morphisms:
                                        abcCompositionFunctor = self.comp[(aZeroCell, bZeroCell, cZeroCell)]
                                        bcdCompositionFunctor = self.comp[(bZeroCell, cZeroCell, dZeroCell)]
                                        abcTwoCellMap = abcCompositionFunctor.morphismMap
                                        bcdTwoCellMap = bcdCompositionFunctor.morphismMap
                                        abcFirst = bcdTwoCellMap[(cdTwoCell, abcTwoCellMap[(bcTwoCell, abTwoCell)])]
                                        bcdFirst = abcTwoCellMap[(bcdTwoCellMap[(cdTwoCell, bcTwoCell)], abTwoCell)]
                                        if abcFirst != bcdFirst:
                                            return False
                                        
        return True


###############   Product Category Functions   ##############
    
# construct c x d 
def productCategory(c:Category, d:Category) -> Category:
    src = srcProduct(c, d)
    target = targetProduct(c, d)
    comp = compProduct(c,d)
    identityMap = identityMapProduct(c,d)
    productCat = Category(src, target, comp, identityMap)
    return productCat

# construct the source dictionary for the product
def srcProduct(c:Category, d:Category) -> dict:
    src = {(m1,m2):(o1, o2) for m1, o1 in c.src.items() for m2,o2 in d.src.items()}
    return src

# construct the target dictionary for the product
def targetProduct(c:Category, d:Category) -> dict:
    target = {(m1,m2):(o1, o2) for m1, o1 in c.target.items() for m2,o2 in d.target.items()}
    return target
    
# construct the composition dictionary for the product    
def compProduct(c:Category, d:Category) -> dict:
    comp = {((m1Source[0],m2Source[0]), (m1Source[1],m2Source[1])):(m1Target, m2Target) for m1Source, m1Target in c.comp.items() for m2Source, m2Target in d.comp.items()}
    return comp

# construct the identity dictionary for the product
def identityMapProduct (c:Category, d:Category) -> dict:
    identityMap = {(ob1, ob2): (id1, id2) for ob1,id1 in c.identityMap.items() for ob2,id2 in d.identityMap.items()}
    return identityMap

# %% [markdown]
# ### Examples: defining categories, the product, and a functor

# %%
# define two identical categories and their product
src = {"f":0, "g":1, "h":2, "i":0, "m":0, "k":1}
target = {"f":1, "g":2, "h":3, "i":2, "m":3, "k":3}
comp = {("g","f"): "i", ("h", "g"):"k", ("h","i"): "m", ("k","f"): "m"}

c1 = Category(src, target, comp, {})
c2 = Category(src, target, comp, {})

productC1C2 = productCategory(c1, c2)

# define the identity functor
objectMap = {0:0, 1:1, 2:2, 3:3}
morphismMap = {i:i for i in c1.morphisms}
F = Functor(c1, c2, objectMap, morphismMap)

# %% [markdown]
# ### To define a strict 2-category:
# 
#     1. specify 0-cells
#     2. specify categories Hom(A,B) for all 0-cells A,B
#     3. specify identity 1-cell in Hom(A,A) for each 0-cell A (identity 2-cell follows automatically)
#     4. specify composition functor Hom(B,C) x Hom(A,B) --> Hom(A,C) respecting identities and associativity

# %%
# define the hom categories as the group Z2

# Notation: 2_00_1 is the 2-cell with source 0 and target 0 and index 1 (actually source/target is 1_0 but we drop the 1-cell notation)
src = {"2_00_1": "1_0", "2_00_0": "1_0"}
target = {"2_00_1": "1_0", "2_00_0": "1_0"}
comp = {("2_00_0", "2_00_0"):"2_00_0", ("2_00_0", "2_00_1"): "2_00_1", ("2_00_1", "2_00_0"): "2_00_1", ("2_00_1", "2_00_1"): "2_00_0"}
z2 = Category(src, target, comp, {"1_0": "2_00_0"})

# Notation: 0_1 is the 0-cell with index 1
zeroCells = ["0_0","0_1"]
hom = {("0_0","0_0"):z2, ("0_1","0_1"):z2, ("0_0", "0_1"):z2}
identityMap = {"0_0":"1_0", "0_1":"1_0"}

# Notation: F001 is the composition functor Hom(0_0, 0_1) x Hom(0_0, 0_0) --> Hom(0_0, 0_1)
F000 = Functor(productCategory(z2,z2), z2, {("1_0","1_0"):"1_0"}, {("2_00_0","2_00_0"): "2_00_0", 
                                                       ("2_00_0", "2_00_1"): "2_00_1", 
                                                       ("2_00_1", "2_00_0"): "2_00_1", 
                                                       ("2_00_1", "2_00_1"): "2_00_0"})
F001 = copy.deepcopy(F000)
F011 = copy.deepcopy(F000)
F111 = copy.deepcopy(F000)

# (C, B, A)
comp = {("0_0","0_0","0_0"):F000, ("0_0","0_0","0_1"):F001, ("0_0","0_1","0_1"):F011, ("0_1","0_1","0_1"): F111}
strict2 = StrictTwoCategory(zeroCells, hom, identityMap, comp)
strict2

# %%
def enumerateFunctors(c:Category, d:Category, numToFind:int = 0) -> list:
    functorList = []
    allFunctions = itertools.product(d.morphisms, repeat=len(c.morphisms))
    for thisFunction in allFunctions:
        morphismMap = dict(zip(c.morphisms, thisFunction))
        objectMap = objectMapFromMorphismMap(c, d, morphismMap)
        try:
            potentialFunctor = Functor(c, d, objectMap, morphismMap)
            functorList.append(potentialFunctor)
            if len(functorList) == numToFind:
                return functorList
        except AssertionError:
            pass
    return functorList

def objectMapFromMorphismMap(c:Category, d:Category, morphismMap:dict) -> dict:
    objectMap = []
    for cMorphism, dMorphism in morphismMap.items():
        srcPair = (c.src[cMorphism], d.src[dMorphism])
        objectMap.append(srcPair)
        targetPair = (c.target[cMorphism], d.target[dMorphism])
        objectMap.append(targetPair)

    objectMap = dict(list(set(objectMap)))
    return objectMap

# %%
functorList = enumerateFunctors(c1, c1, 3)
print(functorList)

# %% [markdown]
# ## Scratch

# %%
'''                
    # add identity morphisms to set of morphisms
    def addIdentities(self) -> None:
        for thisObject in self.objects:
            thisMorphism = "id_" + str(thisObject)
            self.src[thisMorphism] = thisObject
            self.target[thisMorphism] = thisObject
            self.morphisms = self.morphisms + [thisMorphism]
            self.identityMap[thisObject] = thisMorphism
            for i in self.morphisms:
                if self.src[i] == thisObject:
                    self.comp[(i, thisMorphism)] = i
                if self.target[i] == thisObject:
                    self.comp[(thisMorphism, i)] = i
    '''


