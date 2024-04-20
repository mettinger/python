# %%
class Category:
    def __init__(self, src:dict, target:dict, comp:dict, addIdentities:bool = False) -> None:
        self.src = src
        self.target = target
        self.comp = comp
        self.objects = set(src.values()).union(set(target.values()))
        self.morphisms = list(src.keys())

        assert src.keys() == target.keys()
        assert self.composabilityCheck()
        assert self.compositionCheck()
        assert self.associativityCheck()

        if addIdentities:
            self.addIdentities()
        
    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        return str((self.src, self.target, self.comp))

    # Check that all the composables have matching targets and sources.
    def composabilityCheck(self)-> bool:
        for second,first in self.comp.keys():
            if self.target[first] != self.src[second]:
                print("Composability violation...")
                return False
        return True
    
    # Check that any two composable morphisms have a name
    def compositionCheck(self) -> bool:
        for first in self.morphisms:
            for second in self.morphisms:
                if self.src[second] == self.target[first]:
                    if (second, first) not in self.comp.keys():
                        print("Composables lack a name...")
                        return False
        return True
    
    # Check associativity
    def associativityCheck(self) -> bool:
        for first in self.morphisms:
            for second in self.morphisms:
                for third in self.morphisms:
                    if (self.src[third] == self.target[second]) and (self.src[second] == self.target[first]):
                        if self.comp[(third, self.comp[second, first])] != self.comp[(self.comp[third, second], first)]:
                            print("Associativty failure...")
                            return False
        return True
    
    def addIdentities(self) -> None:
        for thisObject in self.objects:
            thisMorphism = "id_" + str(thisObject)
            self.src[thisMorphism] = thisObject
            self.target[thisMorphism] = thisObject
            self.morphisms = self.morphisms + [thisMorphism]
            for i in self.morphisms:
                if self.src[i] == thisObject:
                    self.comp[(i, thisMorphism)] = i
                if self.target[i] == thisObject:
                    self.comp[(thisMorphism, i)] = i


class Functor:
    def __init__(self, srcCat: Category, targetCat: Category, objectMap: dict, morphismMap: dict) -> None:
        self.srcCat = srcCat
        self.targetCat = targetCat
        self.objectMap = objectMap
        self.morphismMap = morphismMap

        assert self.homomorphismFunctorCheck()

    def __str__(self) -> str:
        return str((self.srcCat, self.targetCat, self.objectMap, self.morphismMap))
    
    def homomorphismFunctorCheck(self) -> bool:
        for first in self.srcCat.morphisms:
            srcViolation = self.objectMap[self.srcCat.src[first]] != self.targetCat.src[self.morphismMap[first]]
            targetViolation = self.objectMap[self.srcCat.target[first]] != self.targetCat.target[self.morphismMap[first]]
            if srcViolation or targetViolation:
                print("Functor violation...")
                return False
            for second in self.srcCat.morphisms:
                if self.srcCat.src[second] == self.srcCat.target[first]:
                    srcComp = self.srcCat.comp[(second,first)]
                    targetComp = self.targetCat.comp[(self.morphismMap[second], self.morphismMap[first])]
                    if self.morphismMap[srcComp] != targetComp:
                        print("Functor composition violation...")
                        return False
        return True

# %%
def productCategory(c:Category, d:Category):
    src = srcProduct(c, d)
    target = targetProduct(c, d)
    comp = compProduct(c,d)
    productCat = Category(src, target, comp, addIdentities=False)
    return productCat

def srcProduct(c:Category, d:Category):
    src = {(m1,m2):(o1, o2) for m1, o1 in c.src.items() for m2,o2 in d.src.items()}
    return src

def targetProduct(c:Category, d:Category):
    target = {(m1,m2):(o1, o2) for m1, o1 in c.target.items() for m2,o2 in d.target.items()}
    return target
    
def compProduct(c:Category, d:Category):
    comp = {((m1Source[0],m2Source[0]), (m1Source[1],m2Source[1])):(m1Target, m2Target) for m1Source, m1Target in c.comp.items() for m2Source, m2Target in d.comp.items()}
    return comp

# %%
src = {"f":0, "g":1, "h":2, "i":0, "m":0, "k":1}
target = {"f":1, "g":2, "h":3, "i":2, "m":3, "k":3}
comp = {("g","f"): "i", ("h", "g"):"k", ("h","i"): "m", ("k","f"): "m"}

c1 = Category(src, target, comp, True)
c2 = Category(src, target, comp, True)

productC1C2 = productCategory(c1, c2)

objectMap = {0:0, 1:1, 2:2, 3:3}
morphismMap = {i:i for i in c1.morphisms}
F = Functor(c1, c2, objectMap, morphismMap)

# %%
print(F)


