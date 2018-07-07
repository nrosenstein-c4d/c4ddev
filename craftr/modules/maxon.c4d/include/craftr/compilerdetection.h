#ifdef USE_API_MAXON

#include "../_api_maxon/source/c4d_misc_base_compilerdetection.h"

#else

#ifndef COMPILERDETECTION_H__
#define COMPILERDETECTION_H__

// Target Detection, in case compiler settings are not properly adjusted
#if (__LP64__ || _WIN64) && !defined(MAXON_TARGET_64BIT)
  #define MAXON_TARGET_64BIT
#endif

#if (_WIN32 || _MSC_VER) && !defined(MAXON_TARGET_WINDOWS)
  #define MAXON_TARGET_WINDOWS
#elif (__APPLE__)
  #include <TargetConditionals.h>
  #if TARGET_OS_MAC && (TARGET_OS_IPHONE || TARGET_IPHONE_SIMULATOR) && !defined(MAXON_TARGET_IOS)
    #define MAXON_TARGET_IOS
  #elif TARGET_OS_MAC && !defined(MAXON_TARGET_OSX) && !defined(MAXON_TARGET_IOS)
    #define MAXON_TARGET_OSX
  #elif !defined(MAXON_TARGET_OSX) && !defined(MAXON_TARGET_IOS)
    #error "Unsupported Target"
  #endif
#elif defined(__GNUC__) && !defined(MAXON_TARGET_LINUX)
  #define MAXON_TARGET_LINUX
#elif !defined(MAXON_TARGET_WINDOWS) && !defined(MAXON_TARGET_LINUX)
  #error "Unsupported Target"
#endif

#if !defined(MAXON_TARGET_DEBUG) && !defined(MAXON_TARGET_RELEASE)
  #if !defined(NDEBUG) && (defined(_DEBUG) || (!defined(MAXON_TARGET_WINDOWS) && defined(DEBUG) && DEBUG == 1))
    #define MAXON_TARGET_DEBUG
  #else
    #define MAXON_TARGET_RELEASE
  #endif
#endif

#undef _HAS_STATIC_ASSERT

#if defined(__INTEL_COMPILER) && __INTEL_COMPILER >= 1200 // intel compiler 12.0
  #undef _HAS_NULLPTR             // not supported by intel 12.0
  #define _HAS_MOVE_CONSTRUCTOR   // new feature of intel 12.0
  #ifndef _HAS_DECLTYPE
    #define _HAS_DECLTYPE
  #endif
  #define _HAS_STATIC_ASSERT

  #if __INTEL_COMPILER >= 1210      // intel compiler >= 12.1
    #define _HAS_NULLPTR            // new feature of intel 12.1

// The icc has variadic templates, but you always get warning #1599: declaration hides parameter
//    #define _HAS_VARIADIC_TEMPLATES

    #if __INTEL_COMPILER >= 1300        // intel compiler >= 13
      #define _HAS_EXPLICIT_CONVERSION  // "explicit" new feature of intel 13.0
      #define _HAS_NOEXCEPT
    #endif
  #endif

  #ifdef MAXON_TARGET_LINUX
    #define override  // override specifier not yet supported by Intel compiler 13.0, use empty macro
  #endif

  #define _HAS_DEFAULT_TEMPLATE_FUNCTION_ARGUMENTS

#elif defined(__clang__)
  #define _HAS_MOVE_CONSTRUCTOR
  #define _HAS_NULLPTR
  #if __has_feature(cxx_decltype)
    #define _HAS_DECLTYPE
  #endif
  #if __has_feature(cxx_static_assert)
    #define _HAS_STATIC_ASSERT
  #endif
  #if __has_feature(cxx_default_function_template_args)
    #define _HAS_DEFAULT_TEMPLATE_FUNCTION_ARGUMENTS
  #endif
  #if __has_feature(cxx_variadic_templates)
    #define _HAS_VARIADIC_TEMPLATES
  #endif
  #define _HAS_EXPLICIT_CONVERSION
  #define _HAS_NOEXCEPT
#elif (defined MAXON_TARGET_WINDOWS)

  #define _HAS_NULLPTR
  #define _HAS_MOVE_CONSTRUCTOR
#if _MSC_VER < 1800
  #define _HAS_DECLTYPE
  #define override  // override specifier not yet supported by MSVC, use empty macro
#endif
#if _MSC_VER >= 1900
  #define _HAS_NOEXCEPT
  #pragma warning(disable:4458) // declaration hides class member
  #pragma warning(disable:4577) // 'noexcept' used with no exception handling mode specified
  #pragma warning(disable:4244) // 'return': conversion from 'Type1' to 'Type2', possible loss of data.
#endif
  #define _HAS_STATIC_ASSERT
  #pragma warning(disable:4344) // disable warning: A call to a function using explicit template arguments calls a different function than it would if explicit arguments had not been specified
  #pragma warning(disable:4345) // disable warning: behavior change: an object of POD type constructed with an initializer of the form () will be default-initialized
  #pragma warning(disable:4800) // forcing value to bool 'true' or 'false' (performance warning)

  #if !defined(__INTEL_COMPILER)
    #pragma warning(disable:4512) // disable false warning 'assignment operator could not be generated'
  #endif
#elif defined(__GNUC__)
  #define override // GCC doesn't support override yet
  #if ((__GNUC__ > 4) || (__GNUC_MINOR__ >= 6))
    // GCC >= 4.6 case (will be relevant for Linux)
    #define _HAS_NULLPTR
    #define _HAS_MOVE_CONSTRUCTOR
    #define _HAS_DECLTYPE
    #define _HAS_DEFAULT_TEMPLATE_FUNCTION_ARGUMENTS
    #define _HAS_STATIC_ASSERT
    #define _HAS_NOEXCEPT
  #endif
#endif

#ifdef _HAS_EXPLICIT_CONVERSION
  #define C4D_MISC_OPERATOR_BOOL explicit operator Bool
  #define C4D_MISC_OPERATOR_BOOL_TYPE Bool
  #define C4D_MISC_EXPLICIT_CONVERSION explicit
#else
  #define C4D_MISC_OPERATOR_BOOL operator void*
  #define C4D_MISC_OPERATOR_BOOL_TYPE (void*)
  #define C4D_MISC_EXPLICIT_CONVERSION
#endif

#ifndef _HAS_DECLTYPE
  // try the GCC extension typeof
  #define decltype typeof
#endif

#ifndef _HAS_STATIC_ASSERT
  #define static_assert(cond, str)                            // dummy for old compiler
#endif

#ifndef _HAS_NOEXCEPT
  #define noexcept throw()                                  // compiler doesn't know noexcept yet
#endif

#ifdef _HAS_MOVE_CONSTRUCTOR
  #include <utility>                                        // std::move defined here

  #if !defined(_LIBCPP_UTILITY) && (defined(MAXON_TARGET_OSX) || defined(MAXON_TARGET_IOS)) // workaround for libstdc++ without move support

    #if !(MAXON_TARGET_LINUX && __INTEL_COMPILER >= 1210)
      #include <tr1/type_traits>                            // must use std::tr1 for type traits
    #endif

    namespace std                                           // add required c++11 support to old stdlib
    {
    template <typename T> struct remove_reference { typedef T type; };
    template <typename T> struct remove_reference<T&> { typedef T type; };
    template <typename T> struct remove_reference<T&&> { typedef T type;  };

    // accept either an lvalue or rvalue argument, and return it as an rvalue without triggering a copy construction
    template <typename T> typename remove_reference<T>::type&& move(T &&t)  { return (typename remove_reference<T>::type&&) t; }

    // forward preserves the lvalue/rvalue-ness of the argument.
    template <typename T> T&& forward(typename remove_reference<T>::type& a) { return static_cast<T&&>(a); }

    template <typename T> struct remove_const { typedef T type; };
    template <typename T> struct remove_const<const T> { typedef T type; };

    template <typename T> struct remove_pointer { typedef T type; };
    template <typename T> struct remove_pointer<T*> { typedef T type; };

    // from windows std::lib
    // convenient template for integral constant types
    template<typename _Ty, _Ty _Val> struct integral_constant
    {
      static const _Ty value = _Val;
      typedef _Ty value_type;
      typedef integral_constant<_Ty, _Val> type;
    };

    typedef integral_constant<bool, true> true_type;
    typedef integral_constant<bool, false> false_type;

    template <class _Tp, class _Up> struct is_same           : public false_type {};
    template <class _Tp>            struct is_same<_Tp, _Tp> : public true_type {};

    // TEMPLATE CLASS is_lvalue_reference
    template<typename _Ty> struct is_lvalue_reference : false_type
    { // determine whether _Ty is an lvalue reference
    };

    template<typename _Ty> struct is_lvalue_reference<_Ty&> : true_type
    { // determine whether _Ty is an lvalue reference
    };

    // TEMPLATE CLASS is_rvalue_reference
    template<typename _Ty> struct is_rvalue_reference : false_type
    { // determine whether _Ty is an rvalue reference
    };

    template<typename _Ty> struct is_rvalue_reference<_Ty&&> : true_type
    { // determine whether _Ty is an rvalue reference
    };

    template<bool> struct _Cat_base;
    template<> struct _Cat_base<false> : false_type
    { // base class for type predicates
    };

    template<> struct _Cat_base<true> : true_type
    { // base class for type predicates
    };

    // TEMPLATE CLASS is_reference
    template<typename _Ty> struct is_reference : _Cat_base<is_lvalue_reference<_Ty>::value || is_rvalue_reference<_Ty>::value>
    { // determine whether _Ty is a reference
    };
    // from windows std::lib
    template <typename T> struct is_const : false_type {};
    template <typename T> struct is_const<const T> : true_type {};

    template <typename T> struct __is_pointer__ : false_type {};
    template <typename T> struct __is_pointer__<T*> : true_type {};
    template <typename T> struct is_pointer : __is_pointer__<typename remove_const<T>::type> {};

    template <typename T> struct is_array : false_type {};
    template <typename T> struct is_array<T[]> : true_type {};
    template <typename T, int N> struct is_array<T[N]> : true_type {};

    template <bool B, typename T = void> struct enable_if { typedef T type; };
    template <typename T> struct enable_if<false, T> {};

    #if !(MAXON_TARGET_LINUX && __INTEL_COMPILER >= 1210)
    // add supported type traits to std namespace
    template <typename T> struct is_pod : public std::tr1::is_pod<T> {};
    #else
    template <typename T> struct is_pod { static const bool value = false; };
    #endif

    template <typename T> struct is_scalar : public std::tr1::is_scalar<T> {};

    // add nullptr_t to std namespace
    typedef decltype(nullptr) nullptr_t;
    }
  #else                                                     // stdlib with c++11 support
    #include <type_traits>
  #endif

  // from boost.enable_if.hpp
  template <bool B, typename T = void> struct disable_if_c { typedef T type; };
  template <typename T> struct disable_if_c<true, T> {};
  template <typename COND, typename T = void> struct disable_if : public disable_if_c<COND::value, T> {};
  /// disable if macro to force the compiler to do the right things with overloaded && in templates
  #define DISABLE_IF_REFERENCE(TYPE, RET) typename disable_if< std::is_reference<TYPE>, RET>::type

#else                                                       // no rvalues, dummy methods for move and forward
  #error "Compiler doesn't support move semantics"
#endif

#ifndef _HAS_NULLPTR
  const class NULLPTR
  {
    public:
      template<typename T> operator T*() const  { return 0; }
      template<typename C, typename T>  operator T C::*() const { return 0; }
    private:
      void operator &() const;
  } nullptr = {};
#endif

#ifdef __GNUC__
  #define alignof __alignof__
#else

  // Based on http://llvm.org/docs/doxygen/html/AlignOf_8h_source.html
  // The alignment calculated is the minimum alignment, and not necessarily
  // the "desired" alignment returned by GCC's __alignof__ (for example).
  template <typename T> class AlignOf
  {
  private:
    template <typename C> struct AlignmentCalcImpl
    {
      char x;
      C t;
    private:
      AlignmentCalcImpl() {} // Never instantiate.
    };
  public:
    enum
    {
      ALIGNMENT = static_cast<unsigned int>(sizeof(AlignmentCalcImpl<T>) - sizeof(T))
    };
  };

  #define alignof(C)  AlignOf<C>::ALIGNMENT

#endif

#endif // COMPILERDETECTION_H__

#endif
