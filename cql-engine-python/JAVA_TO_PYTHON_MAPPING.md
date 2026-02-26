# Java to Python Mapping Reference

This document provides a detailed mapping of Java classes and methods to their Python equivalents.

## Class Mappings

### CqlType (Interface → Protocol)

| Java | Python |
|------|--------|
| `interface CqlType` | `class CqlType(Protocol):` |
| `Boolean equivalent(Object other)` | `def equivalent(self, other: Any) -> bool:` |
| `Boolean equal(Object other)` | `def equal(self, other: Any) -> bool \| None:` |

### Precision (Enum)

| Java | Python |
|------|--------|
| `enum Precision { YEAR, MONTH, ... }` | `class Precision(Enum):` |
| `YEAR, MONTH, WEEK, DAY, HOUR, MINUTE, SECOND, MILLISECOND` | Same enum values |
| `public ChronoField toChronoField()` | Removed (Python handles internally) |
| `public ChronoUnit toChronoUnit()` | Removed (Python handles internally) |
| `public int toDateIndex()` | `def to_date_index(self) -> int:` |
| `public int toDateTimeIndex()` | `def to_datetime_index(self) -> int:` |
| `public int toTimeIndex()` | `def to_time_index(self) -> int:` |
| `public static Precision fromString(String)` | `@staticmethod def from_string(precision_str: str) -> Precision:` |
| `public static Precision fromDateIndex(int)` | `@staticmethod def from_date_index(index: int) -> Precision:` |
| `public static Precision fromDateTimeIndex(int)` | `@staticmethod def from_datetime_index(index: int) -> Precision:` |
| `public static Precision fromTimeIndex(int)` | `@staticmethod def from_time_index(index: int) -> Precision:` |

### TemporalHelper (Utility Class)

| Java Method | Python Method |
|-------------|---------------|
| `static String[] normalizeDateTimeElements(int...)` | `@staticmethod normalize_datetime_elements(elements: Tuple[int, ...]) -> List[str]:` |
| `static String[] normalizeTimeElements(int...)` | `@staticmethod normalize_time_elements(elements: Tuple[int, ...]) -> List[str]:` |
| `static String addLeadingZeroes(int, int)` | `@staticmethod add_leading_zeros(element: int, length: int) -> str:` |
| `static String autoCompleteDateTimeString(String, Precision)` | `@staticmethod auto_complete_datetime_string(date_string: str, precision: Precision) -> str:` |
| `static String autoCompleteDateString(String, Precision)` | `@staticmethod auto_complete_date_string(date_string: str, precision: Precision) -> str:` |
| `static String autoCompleteTimeString(String, Precision)` | `@staticmethod auto_complete_time_string(time_string: str, precision: Precision) -> str:` |
| `static BigDecimal zoneToOffset(ZoneOffset)` | `@staticmethod zone_to_offset(zone_offset: timezone) -> Decimal:` |
| `static int weeksToDays(int)` | `@staticmethod weeks_to_days(weeks: int) -> int:` |

### BaseTemporal (Abstract Base Class)

| Java | Python |
|------|--------|
| `abstract class BaseTemporal implements CqlType` | `class BaseTemporal(CqlType, ABC):` |
| `private Precision precision` | `precision: Optional[Precision]` (in `__slots__`) |
| `ZoneOffset evaluationOffset` | `evaluation_offset: Optional[timezone]` (in `__slots__`) |
| `public Precision getPrecision()` | `def get_precision(self) -> Optional[Precision]:` |
| `public BaseTemporal setPrecision(Precision)` | `def set_precision(self, precision: Precision) -> BaseTemporal:` |
| `public ZoneOffset getEvaluationOffset()` | `def get_evaluation_offset(self) -> Optional[timezone]:` |
| `public void setEvaluationOffset(ZoneOffset)` | `def set_evaluation_offset(self, offset: timezone) -> None:` |
| `abstract Integer compare(BaseTemporal, boolean)` | `@abstractmethod def compare(self, other: BaseTemporal, for_sort: bool) -> Optional[int]:` |
| `abstract Integer compareToPrecision(...)` | `@abstractmethod def compare_to_precision(...) -> Optional[int]:` |
| `abstract boolean isUncertain(Precision)` | `@abstractmethod def is_uncertain(self, p: Precision) -> bool:` |
| `abstract Interval getUncertaintyInterval(Precision)` | `@abstractmethod def get_uncertainty_interval(self, p: Precision) -> Interval:` |

### Date

| Java | Python |
|------|--------|
| `class Date extends BaseTemporal` | `class Date(BaseTemporal):` |
| `private LocalDate date` | `_date: py_date` (in `__slots__`) |
| `public LocalDate getDate()` | `def get_date(self) -> py_date:` |
| `public void setDate(LocalDate)` | `def set_date(self, date_val: py_date) -> Date:` |
| `public Date(int year)` | `Date(2021)` |
| `public Date(int, int)` | `Date(2021, 5)` |
| `public Date(int, int, int)` | `Date(2021, 5, 15)` |
| `public Date(LocalDate)` | `Date(py_date(2021, 5, 15))` |
| `public Date(String)` | `Date("2021-05-15")` |
| `public Date(LocalDate, Precision)` | `Date(py_date(2021, 5, 15), Precision.DAY)` |

### DateTime

| Java | Python |
|------|--------|
| `class DateTime extends BaseTemporal` | `class DateTime(BaseTemporal):` |
| `private OffsetDateTime dateTime` | `_datetime: py_datetime` (in `__slots__`) |
| `public OffsetDateTime getDateTime()` | `def get_datetime(self) -> py_datetime:` |
| `public void setDateTime(OffsetDateTime)` | `def set_datetime(self, dt: py_datetime) -> DateTime:` |
| `public DateTime withDateTime(OffsetDateTime)` | `def with_datetime(self, dt: py_datetime) -> DateTime:` |
| `public DateTime withPrecision(Precision)` | `def with_precision(self, precision: Precision) -> DateTime:` |
| `public DateTime(OffsetDateTime)` | `DateTime(tz_aware_datetime)` |
| `public DateTime(OffsetDateTime, Precision)` | `DateTime(tz_aware_datetime, Precision.SECOND)` |
| `public DateTime(String, ZoneOffset)` | `DateTime("2021-05-15T14:30:00", timezone.utc)` |

### Time

| Java | Python |
|------|--------|
| `class Time extends BaseTemporal` | `class Time(BaseTemporal):` |
| `private LocalTime time` | `_time: py_time` (in `__slots__`) |
| `public LocalTime getTime()` | `def get_time(self) -> py_time:` |
| `public Time withTime(LocalTime)` | `def with_time(self, time_val: py_time) -> Time:` |
| `public Time withPrecision(Precision)` | `def with_precision(self, precision: Precision) -> Time:` |
| `public Time(LocalTime, Precision)` | `Time(py_time(14, 30, 0), Precision.SECOND)` |
| `public Time(String)` | `Time("14:30:00.123")` |
| `public Time(int...)` | `Time(14, 30, 0, 123)` |

### Quantity

| Java | Python |
|------|--------|
| `class Quantity implements CqlType` | `@dataclass class Quantity(CqlType):` |
| `private BigDecimal value` | `value: Decimal` |
| `private String unit` | `unit: str` |
| `public BigDecimal getValue()` | `quantity.value` (direct attribute) |
| `public void setValue(BigDecimal)` | `quantity.value = ...` |
| `public Quantity withValue(BigDecimal)` | `def with_value(self, value: Decimal \| int \| float \| str) -> Quantity:` |
| `public Quantity withUnit(String)` | `def with_unit(self, unit: str) -> Quantity:` |
| `public boolean unitsEqual(String, String)` | `@staticmethod def units_equal(left_unit: str, right_unit: str) -> bool:` |
| `public boolean unitsEquivalent(...)` | `@staticmethod def units_equivalent(...) -> bool:` |
| `public int compareTo(Quantity)` | `def __lt__, __le__, __gt__, __ge__(self, other: Quantity) -> bool:` |

### Ratio

| Java | Python |
|------|--------|
| `class Ratio implements CqlType` | `@dataclass class Ratio(CqlType):` |
| `private Quantity numerator` | `numerator: Optional[Quantity]` |
| `private Quantity denominator` | `denominator: Optional[Quantity]` |
| `public Quantity getNumerator()` | `ratio.numerator` |
| `public Ratio setNumerator(Quantity)` | `def set_numerator(self, numerator: Quantity) -> Ratio:` |
| `public Quantity getDenominator()` | `ratio.denominator` |
| `public Ratio setDenominator(Quantity)` | `def set_denominator(self, denominator: Quantity) -> Ratio:` |

### Code

| Java | Python |
|------|--------|
| `class Code implements CqlType` | `@dataclass class Code(CqlType):` |
| `private String code` | `code: Optional[str]` |
| `private String display` | `display: Optional[str]` |
| `private String system` | `system: Optional[str]` |
| `private String version` | `version: Optional[str]` |
| `public String getCode()` | `code.code` (direct attribute) |
| `public Code withCode(String)` | `def with_code(self, code: str) -> Code:` |
| `public String getDisplay()` | `code.display` |
| `public Code withDisplay(String)` | `def with_display(self, display: str) -> Code:` |
| `public String getSystem()` | `code.system` |
| `public Code withSystem(String)` | `def with_system(self, system: str) -> Code:` |

### Vocabulary (Abstract Base)

| Java | Python |
|------|--------|
| `abstract class Vocabulary implements CqlType` | `@dataclass class Vocabulary(CqlType):` |
| `private String id` | `id: Optional[str]` |
| `private String version` | `version: Optional[str]` |
| `private String name` | `name: Optional[str]` |
| `public String getId()` | `vocabulary.id` |
| `public void setId(String)` | `def set_id(self, id: str) -> None:` |
| `public String getVersion()` | `vocabulary.version` |
| `public void setVersion(String)` | `def set_version(self, version: str) -> None:` |
| `public String getName()` | `vocabulary.name` |
| `public void setName(String)` | `def set_name(self, name: str) -> None:` |

### CodeSystem

| Java | Python |
|------|--------|
| `class CodeSystem extends Vocabulary` | `class CodeSystem(Vocabulary):` |
| `public CodeSystem withId(String)` | `def with_id(self, id: str) -> CodeSystem:` |
| `public CodeSystem withVersion(String)` | `def with_version(self, version: str) -> CodeSystem:` |
| `public CodeSystem withName(String)` | `def with_name(self, name: str) -> CodeSystem:` |

### Concept

| Java | Python |
|------|--------|
| `class Concept implements CqlType` | `@dataclass class Concept(CqlType):` |
| `private List<Code> codes` | `codes: list[Code]` |
| `private String display` | `display: Optional[str]` |
| `public Iterable<Code> getCodes()` | `concept.codes` (direct access) |
| `public void setCodes(Iterable<Code>)` | `def set_codes(self, codes: Optional[Iterable[Code]]) -> None:` |
| `public Concept withCodes(Iterable<Code>)` | `def with_codes(self, codes: Iterable[Code]) -> Concept:` |
| `public Concept withCode(Code)` | `def with_code(self, code: Code) -> Concept:` |

### ValueSet

| Java | Python |
|------|--------|
| `class ValueSet extends Vocabulary` | `@dataclass class ValueSet(Vocabulary):` |
| `private List<CodeSystem> codeSystems` | `code_systems: list[CodeSystem]` |
| `public Iterable<CodeSystem> getCodeSystems()` | `value_set.code_systems` |
| `public void setCodeSystems(List<CodeSystem>)` | `def set_code_systems(self, code_systems: Optional[Iterable[CodeSystem]]) -> None:` |
| `public void addCodeSystem(CodeSystem)` | `def add_code_system(self, code_system: CodeSystem) -> None:` |
| `public CodeSystem getCodeSystem(String)` | `def get_code_system(self, id: str, version: Optional[str] = None) -> Optional[CodeSystem]:` |
| `public CodeSystem getCodeSystem(String, String)` | Same method (Python overloading via optional params) |

### Tuple

| Java | Python |
|------|--------|
| `class Tuple implements CqlType` | `@dataclass class Tuple(CqlType):` |
| `protected LinkedHashMap<String, Object>` | `elements: OrderedDict[str, Any]` |
| `private Context context` | `context: Optional[Any]` |
| `public Object getElement(String)` | `def get_element(self, key: str) -> Any:` |
| `public HashMap<String, Object> getElements()` | `tuple.elements` (direct access) |
| `public void setElements(LinkedHashMap<...>)` | `def set_elements(self, elements: OrderedDict[str, Any]) -> None:` |

### Interval

| Java | Python |
|------|--------|
| `class Interval implements CqlType` | `@dataclass class Interval(CqlType):` |
| `private Object low` | `low: Any` |
| `private boolean lowClosed` | `low_closed: bool` |
| `private Object high` | `high: Any` |
| `private boolean highClosed` | `high_closed: bool` |
| `private Context context` | `context: Optional[Any]` |
| `public Object getLow()` | `interval.low` |
| `public boolean getLowClosed()` | `interval.low_closed` |
| `public Object getHigh()` | `interval.high` |
| `public boolean getHighClosed()` | `interval.high_closed` |
| `public Class<?> getPointType()` | `interval.point_type` |
| `public Object getStart()` | `def get_start(self) -> Any:` |
| `public Object getEnd()` | `def get_end(self) -> Any:` |
| `public static Object getSize(Object, Object)` | `@staticmethod def get_size(start: Any, end: Any) -> Any:` |

### Value (Utility Class)

| Java | Python |
|------|--------|
| `class Value` | `class Value:` |
| `public static final Integer MAX_INT` | `MAX_INT = 2147483647` |
| `public static final Long MAX_LONG` | `MAX_LONG = 9223372036854775807` |
| `public static final BigDecimal MAX_DECIMAL` | `MAX_DECIMAL = Decimal("...")` |
| `public static BigDecimal verifyPrecision(...)` | `@staticmethod def verify_precision(...) -> Decimal:` |
| `public static BigDecimal validateDecimal(...)` | `@staticmethod def validate_decimal(...) -> Optional[Decimal]:` |
| `public static Integer validateInteger(...)` | `@staticmethod def validate_integer(...) -> Optional[int]:` |
| `public static Long validateLong(...)` | `@staticmethod def validate_long(...) -> Optional[int]:` |

### CqlList (Utility Class)

| Java | Python |
|------|--------|
| `class CqlList` | `class CqlList(Generic[T]):` |
| `private Context context` | `context: Optional[Any]` |
| `private String alias` | `alias: Optional[str]` |
| `public Comparator<Object> valueSort` | `def value_sort(self, left: Any, right: Any) -> int:` |
| `public Comparator<Object> expressionSort` | `def expression_sort(self, left: Any, right: Any) -> int:` |
| `public Comparator<Object> columnSort` | `def column_sort(self, left: Any, right: Any) -> int:` |
| `public int compareTo(Object, Object)` | `@staticmethod def compare_to(left: Any, right: Any) -> int:` |
| `public static Boolean equivalent(...)` | `@staticmethod def equivalent(left: Iterable[Any], right: Iterable[Any], context: Optional[Any] = None) -> bool:` |
| `public static Boolean equal(...)` | `@staticmethod def equal(left: Iterable[Any], right: Iterable[Any], context: Optional[Any] = None) -> Optional[bool]:` |
| `public static <T> List<T> toList(...)` | `@staticmethod def to_list(iterable: Iterable[T], include_null_elements: bool = False) -> list[T]:` |

### Iterator Classes

#### ResetIterator

| Java | Python |
|------|--------|
| `class ResetIterator<E> implements Iterator<E>` | `class ResetIterator(Iterator[T], Generic[T]):` |
| `private Iterator<E> source` | `source: Iterator[T]` |
| `private ArrayList<E> data` | `data: List[T]` |
| `int dataIndex` | `data_index: int` |
| `private boolean dataCached` | `data_cached: bool` |
| `public boolean hasNext()` | `def __next__(self) -> T:` (combined in one method) |
| `public E next()` | `def __next__(self) -> T:` |
| `public void reset()` | `def reset(self) -> None:` |

#### TimesIterator

| Java | Python |
|------|--------|
| `class TimesIterator implements Iterator<Object>` | `class TimesIterator(Iterator[Any]):` |
| `private Iterator<Object> left` | `left: Iterator[Any]` |
| `private ResetIterator<Object> right` | `right: ResetIterator[Any]` |
| `private boolean leftNeeded` | `left_needed: bool` |
| `private Object leftElement` | `left_element: Any` |
| `public boolean hasNext()` | `def has_next(self) -> bool:` |
| `public Object next()` | `def __next__(self) -> Any:` |

#### QueryIterator

| Java | Python |
|------|--------|
| `class QueryIterator implements Iterator<Object>` | `class QueryIterator(Iterator[List[Any]]):` |
| `private Iterator<Object> sourceIterator` | `source_iterator: Iterator[Any]` |
| `private ArrayList<Object> result` | `result: List[Any]` |
| `public boolean hasNext()` | `def __next__(self) -> List[Any]:` |
| `public Object next()` | `def __next__(self) -> List[Any]:` |
| `private Object unpack(Object)` | `def unpack(self, element: Any) -> List[Any]:` |
| `private void unpair(...)` | `@staticmethod def _unpair(...) -> None:` |

## Type Conversions

| Java Type | Python Type |
|-----------|-------------|
| `boolean` | `bool` |
| `int` | `int` |
| `long` | `int` (Python 3 has unlimited int) |
| `float` | `float` |
| `double` | `float` |
| `String` | `str` |
| `BigDecimal` | `Decimal` (from decimal module) |
| `LocalDate` | `date` (from datetime module) |
| `LocalTime` | `time` (from datetime module) |
| `OffsetDateTime` | `datetime` (from datetime module) |
| `ZoneOffset` | `timezone` (from datetime module) |
| `Iterable<T>` | `Iterable[T]` |
| `Iterator<T>` | `Iterator[T]` |
| `List<T>` | `list[T]` or `List[T]` |
| `HashMap<K, V>` | `dict[K, V]` |
| `LinkedHashMap<K, V>` | `OrderedDict[K, V]` |
| `ArrayList<T>` | `list[T]` |
| `Optional<T>` (Java) | `Optional[T]` or `T \| None` |
| `null` | `None` |

## Method Naming Conventions

| Java Pattern | Python Pattern | Example |
|--------------|----------------|---------|
| `getXxx()` | `xxx` property or `get_xxx()` method | `getDate()` → `date` or `get_date()` |
| `setXxx(val)` | `xxx = val` or `set_xxx(val)` method | `setDate(d)` → `date = d` or `set_date(d)` |
| `withXxx(val)` | `with_xxx(val)` method | `withCode()` → `with_code()` |
| `isXxx()` | `is_xxx()` method | `isUncertain()` → `is_uncertain()` |
| `hasXxx()` | `has_xxx()` method | No examples in code |
| `toXxx()` | `to_xxx()` method | `toDateIndex()` → `to_date_index()` |
| `fromXxx()` | `from_xxx()` static method | `fromDateIndex()` → `from_date_index()` |

## Attribute Access Patterns

### Java Pattern
```java
public class Date {
    private LocalDate date;
    public LocalDate getDate() { return date; }
    public void setDate(LocalDate d) { this.date = d; }
}
```

### Python Pattern (Multiple Options)

**Option 1: Direct Attribute Access**
```python
class Date:
    def __init__(self):
        self._date = None  # Name mangling

    # Direct access via public interface
```

**Option 2: Getter/Setter Methods**
```python
class Date:
    def get_date(self) -> date:
        return self._date

    def set_date(self, d: date) -> None:
        self._date = d
```

**Option 3: Properties (Pythonic)**
```python
class Date:
    @property
    def date(self) -> date:
        return self._date

    @date.setter
    def date(self, d: date) -> None:
        self._date = d
```

**Used in Conversion:** Combination of options depending on context - direct attributes where appropriate (dataclasses), methods for validation, properties for convenience.

---

This mapping ensures complete fidelity to the original Java implementation while leveraging Python's modern features and idioms.
