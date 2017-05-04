/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file src_internal/scene_hook.cpp

#include <c4d.h>

enum
{
  C4D_APEX_ID = 1035360,
};

/// --------------------------------------------------------------------------
/// --------------------------------------------------------------------------
class ApexHook : public SceneHookData
{
  public:
    ApexHook() : SceneHookData() { }
    virtual ~ApexHook() { }
    static NodeData* Alloc() { return NewObjClear(ApexHook); }
    virtual Bool Message(GeListNode* node, Int32 msg, void* pdata) override;
};

/// --------------------------------------------------------------------------
/// --------------------------------------------------------------------------
Bool ApexHook::Message(GeListNode* node, Int32 msg, void* pdata)
{
  switch (msg) {
    case MSG_DOCUMENTINFO:
    case MSG_MULTI_RENDERNOTIFICATION:
      GePluginMessage(msg, pdata);
      return true;
  }
  return SceneHookData::Message(node, msg, pdata);
}

/// --------------------------------------------------------------------------
/// --------------------------------------------------------------------------
Bool RegisterApexSceneHook()
{
  const Int32 flags = PLUGINFLAG_SCENEHOOK_NOTDRAGGABLE;
  const Int32 disklevel = 0;
  const Int32 priority = 0;
  return RegisterSceneHookPlugin(
    C4D_APEX_ID, "c4d_apex", flags, ApexHook::Alloc,
    priority, disklevel, nullptr);
}
