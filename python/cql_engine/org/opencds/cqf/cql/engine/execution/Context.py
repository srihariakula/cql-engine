"""Auto-generated Python scaffold from Java source.

Source: engine/src/main/java/org/opencds/cqf/cql/engine/execution/Context.java
"""

class Context:
    def removeEldestEntry(self, MapEntryVersionedIdentifier, LinkedHashMapString, eldestEntry):
        raise NotImplementedError("Port from Java implementation is pending")

    def constructLibraryExpressionHashMap(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def getEvaluatedResources(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def clearEvaluatedResources(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def pushEvaluatedResourceStack(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def popEvaluatedResourceStack(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def getDebugMap(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def setDebugMap(self, debugMap):
        raise NotImplementedError("Port from Java implementation is pending")

    def getDebugResult(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def shouldDebug(self, e):
        raise NotImplementedError("Port from Java implementation is pending")

    def ensureDebugResult(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def clearExpressions(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def logDebugResult(self, node, result, action):
        raise NotImplementedError("Port from Java implementation is pending")

    def logDebugMessage(self, locator, message):
        raise NotImplementedError("Port from Java implementation is pending")

    def logDebugWarning(self, locator, message):
        raise NotImplementedError("Port from Java implementation is pending")

    def logDebugTrace(self, locator, message):
        raise NotImplementedError("Port from Java implementation is pending")

    def logDebugError(self, e):
        raise NotImplementedError("Port from Java implementation is pending")

    def init(self, library, systemDataProvider, ucumService):
        raise NotImplementedError("Port from Java implementation is pending")

    def setEvaluationDateTime(self, evaluationZonedDateTime):
        raise NotImplementedError("Port from Java implementation is pending")

    def getEvaluationZonedDateTime(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def getEvaluationOffsetDateTime(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def getEvaluationDateTime(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def getUcumService(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def getSharedUcumService(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def setExpressionCaching(self, yayOrNay):
        raise NotImplementedError("Port from Java implementation is pending")

    def getCacheForLibrary(self, libraryId):
        raise NotImplementedError("Port from Java implementation is pending")

    def isExpressionCached(self, libraryId, name):
        raise NotImplementedError("Port from Java implementation is pending")

    def isExpressionCachingEnabled(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def cacheExpression(self, libraryId, name, er):
        raise NotImplementedError("Port from Java implementation is pending")

    def getCachedExpression(self, libraryId, name):
        raise NotImplementedError("Port from Java implementation is pending")

    def registerLibraryLoader(self, libraryLoader):
        raise NotImplementedError("Port from Java implementation is pending")

    def getCurrentLibrary(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolveIncludeDef(self, includeDef):
        raise NotImplementedError("Port from Java implementation is pending")

    def enterLibrary(self, libraryName):
        raise NotImplementedError("Port from Java implementation is pending")

    def exitLibrary(self, enteredLibrary):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolveCodeRef(self, name):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolveConceptRef(self, name):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolveLibraryRef(self, libraryName):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolveExpressionRef(self, name):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolveIdentifierRef(self, name):
        raise NotImplementedError("Port from Java implementation is pending")

    def fixupQName(self, typeName):
        raise NotImplementedError("Port from Java implementation is pending")

    def createInstance(self, typeName):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolveType(self, typeName):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolveOperandType(self, operandDef):
        raise NotImplementedError("Port from Java implementation is pending")

    def is_(self, operand, type_):
        raise NotImplementedError("Port from Java implementation is pending")

    def as_(self, operand, type_, isStrict):
        raise NotImplementedError("Port from Java implementation is pending")

    def isType(self, argumentType, operandType):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolveFunctionRef(self, functionDef, arguments):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolveParameterRef(self, name):
        raise NotImplementedError("Port from Java implementation is pending")

    def setParameter(self, libraryName, name, value):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolveValueSetRef(self, name):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolveCodeSystemRef(self, name):
        raise NotImplementedError("Port from Java implementation is pending")

    def registerDataProvider(self, modelUri, dataProvider):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolveDataProvider(self, dataType):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolveDataProviderByModelUri(self, modelUri):
        raise NotImplementedError("Port from Java implementation is pending")

    def registerTerminologyProvider(self, tp):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolveTerminologyProvider(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def registerExternalFunctionProvider(self, identifier, provider):
        raise NotImplementedError("Port from Java implementation is pending")

    def getExternalFunctionProvider(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def enterContext(self, context):
        raise NotImplementedError("Port from Java implementation is pending")

    def exitContext(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def getCurrentContext(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def setContextValue(self, context, contextValue):
        raise NotImplementedError("Port from Java implementation is pending")

    def hasContextValueChanged(self, context, contextValue):
        raise NotImplementedError("Port from Java implementation is pending")

    def getCurrentContextValue(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def push(self, variable):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolveVariable(self, name):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolveAlias(self, name):
        raise NotImplementedError("Port from Java implementation is pending")

    def pop(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def pushWindow(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def popWindow(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def getStack(self):
        raise NotImplementedError("Port from Java implementation is pending")

    def resolvePath(self, target, path):
        raise NotImplementedError("Port from Java implementation is pending")

    def setValue(self, target, path, value):
        raise NotImplementedError("Port from Java implementation is pending")

    def objectEqual(self, left, right):
        raise NotImplementedError("Port from Java implementation is pending")

    def objectEquivalent(self, left, right):
        raise NotImplementedError("Port from Java implementation is pending")
