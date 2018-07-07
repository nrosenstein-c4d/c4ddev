/////////////////////////////////////////////////////////////
// CINEMA 4D SDK                                           //
/////////////////////////////////////////////////////////////
// (c) MAXON Computer GmbH, all rights reserved            //
/////////////////////////////////////////////////////////////

#ifndef LEGACY_H__
#define LEGACY_H__

#include "c4d.h"
#include "vector4.h"
#include "matrix4.h"

// Added by Niklas Rosenstein 2016/11/26
#define RealToString String::FloatToString
#define LongToString(x) String::IntToString((Int32) x)
#define PtrToString String::HexToString
#define MemoryToString String::MemoryToString

typedef Char			CHAR;
typedef UChar			UCHAR;
typedef Int16			SWORD;
typedef UInt16		UWORD;

typedef Int32			LONG;
typedef UInt32		ULONG;

typedef Int64			LLONG;
typedef UInt64		LULONG;
typedef Int				VLONG;
typedef UInt			VULONG;

typedef Float			Real;
typedef Float32		SReal;
typedef Float64		LReal;

typedef Vector32	SVector;
typedef Vector64	LVector;

typedef Matrix32	SMatrix;
typedef Matrix64	LMatrix;

typedef Vector4d32	SVector4;
typedef Vector4d64	LVector4;
typedef Vector4d		Vector4;

typedef Matrix4d32	SMatrix4;
typedef Matrix4d64	LMatrix4;
typedef Matrix4d		Matrix4;

#if defined MAXON_TARGET_OSX
	inline Float32 Ln10(Float32 val) { return log10f(val); }
	inline Float64 Ln10(Float64 val) { return log10(val); }

	inline Float32 Ld(Float32 val) { return log2f(val); }
	inline Float64 Ld(Float64 val) { return log2(val); }
#else
	inline Float32 Ln10(Float32 val) { return log10(val); }
	inline Float64 Ln10(Float64 val) { return log10(val); }

	inline Float32 Ld(Float32 val) { return log(val) * 1.4426950408889634073599246810019f; }
	inline Float64 Ld(Float64 val) { return log(val) * 1.4426950408889634073599246810019; }
#endif

#undef MAXLONG // Windows header have MINLONG defines as 0x80000000
#undef MINLONG // Windows header have MINLONG defines as 0x80000000

#define MAXLONGl					0x7fffffff
#define MAXLONGf					2147483520.0f		// 0x7FFFFF80 - rounding MAXLONG to Real results in 0x80000000
#define MAXLONGd					Float64(MAXLONGl)
#define MINLONGl					(-0x7fffffff)		// Explicitly not 0x80000000
#define MINLONGf					-2147483520.0f	// -0x7FFFFF80 - rounding MINLONG to Real results in 0x80000000
#define MINLONGd					Float64(MINLONGl)

#ifndef MAXULONG
	#define MAXULONG				0xffffffff
#endif
#ifndef MAXSWORD
	#define MAXSWORD				32767L
#endif
#ifndef MAXUWORD
	#define MAXUWORD				65535L
#endif

#define MAXREALs					( 9.0e18f)
#define MINREALs					(-9.0e18f)

#define MAXREALr					( 1.0e308)
#define MINREALr					(-1.0e308)

#define MAXREALl					( 1.0e308)
#define MINREALl					(-1.0e308)

#define SCO	(Float32)
#define RCO	(Float)
#define LCO	(Float64)

#define pi			PI
#define piinv		PI_INV
#define pi2			PI2
#define pi2inv	PI2_INV
#define pi05		PI05
#define pi05inv (PI_INV * 2.0)

#define FtoL(x)	Int32(x)

inline Int32 SAFELONG(Float32 x)	{ return SAFEINT32(x); }
inline Int32 SAFELONG(Float64 x)	{ return SAFEINT32(x); }

inline Int32 LFloor(Float32 r)	{ return Int32(Floor(r)); }
inline Int32 LCeil(Float32 r)		{ return Int32(Ceil(r));  }
inline Int32 LFloor(Float64 r)	{ return Int32(Floor(r)); }
inline Int32 LCeil(Float64 r)		{ return Int32(Ceil(r));  }

inline Float32 FCut01(Float32 a)	{ return Clamp01(a); }
inline Float64 FCut01(Float64 a)	{ return Clamp01(a); }

#define c4d_misc maxon

#define LMatrixToHPB Matrix64ToHPB

#define SetLong				SetInt32
#define SetULong			SetUInt32
#define SetLLong			SetInt64
#define SetUInt64			SetUInt64
#define SetReal				SetFloat

#define GetLong				GetInt32
#define GetULong			GetUInt32
#define GetLLong			GetInt64
#define GetUInt64			GetUInt64
#define GetReal				GetFloat

#define ReadWord			ReadInt16
#define ReadUWord			ReadUInt16
#define ReadLong			ReadInt32
#define ReadULong			ReadUInt32
#define ReadLLong			ReadInt64
#define ReadLULong		ReadUInt64
#define ReadReal			ReadFloat
#define ReadSReal			ReadFloat32
#define ReadLReal			ReadFloat64
#define ReadSVector		ReadVector32
#define ReadLVector		ReadVector64
#define ReadSMatrix		ReadMatrix32
#define ReadLMatrix		ReadMatrix64

#define WriteWord			WriteInt16
#define WriteUWord		WriteUInt16
#define WriteLong			WriteInt32
#define WriteULong		WriteUInt32
#define WriteLLong		WriteInt64
#define WriteLULong		WriteUInt64
#define WriteReal			WriteFloat
#define WriteSReal		WriteFloat32
#define WriteLReal		WriteFloat64
#define WriteSVector	WriteVector32
#define WriteLVector	WriteVector64
#define WriteSMatrix	WriteMatrix32
#define WriteLMatrix	WriteMatrix64

#define GetLengthSquared GetSquaredLength
#define GeBoom CriticalStop
#define GeAssert DebugAssert
#define GeBreak CriticalStop

#define MemoryPool DeprecatedMemoryPool
#define ToLong ParseToInt32
#define ToReal ParseToFloat
#define FORMAT_LONG FORMAT_INT
#define FORMAT_REAL FORMAT_FLOAT
#define HYPERFILEVALUE_WORD			HYPERFILEVALUE_INT16
#define HYPERFILEVALUE_UWORD		HYPERFILEVALUE_UINT16
#define HYPERFILEVALUE_LONG			HYPERFILEVALUE_INT32
#define HYPERFILEVALUE_ULONG		HYPERFILEVALUE_UINT32
#define HYPERFILEVALUE_LLONG		HYPERFILEVALUE_INT64
#define HYPERFILEVALUE_LULONG		HYPERFILEVALUE_UINT64
#define HYPERFILEVALUE_REAL			HYPERFILEVALUE_FLOAT
#define HYPERFILEVALUE_LREAL		HYPERFILEVALUE_FLOAT64
#define HYPERFILEVALUE_LVECTOR	HYPERFILEVALUE_VECTOR64
#define HYPERFILEVALUE_LMATRIX	HYPERFILEVALUE_MATRIX64
#define HYPERFILEVALUE_SVECTOR	HYPERFILEVALUE_VECTOR32
#define HYPERFILEVALUE_SMATRIX	HYPERFILEVALUE_MATRIX32
#define HYPERFILEVALUE_SREAL		HYPERFILEVALUE_FLOAT32
#define LV_RES_LONG	LV_RES_INT
#define DESC_UNIT_LONG	DESC_UNIT_INT
#define DESC_UNIT_REAL	DESC_UNIT_FLOAT
#define CGetLong	CGetInt
#define CGetReal	CGetFloat
#define SetOMLong	SetOMInt
#define GetOMLong	GetOMInt
#define SetOMReal	SetOMFloat
#define GetOMReal	GetOMFloat
#define VectorEqual(a, b) (a).IsEqual(b)
#define CutColor(a) (a).Clamp01()
#define VectorSum(a) (a).GetSum()
#define VectorGray(a) (a).GetAverage()
#define VectorAngle GetAngle
#define VectorMin(a) (a).GetMin()
#define VectorMax(a) (a).GetMax()
#define Mix Blend
#define Step StepEx
#define FCut ClampValue
#define Ln10 Log10
#define Ld Log2
#define FCut01 Clamp01

#define C4D_MISC_FORWARD_PARAMETER(T)	T&&
#define C4D_MISC_MOVE_TYPE(T)					T&&
#define C4D_MISC_MOVE_BASE_CLASS(src, ...)	__VA_ARGS__(std::move(src))

#define gNew(x) NewObj(x)

#ifdef MAXON_TARGET_64BIT
	#define __C4D_64BIT
#endif

#endif // LEGACY_H__
