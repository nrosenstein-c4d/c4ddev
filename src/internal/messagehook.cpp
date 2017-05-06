/// Copyright (C) 2015 Niklas Rosenstein
/// All rights reserved.
///
/// \file src_internal/scene_hook.cpp

#include <c4d.h>

enum {
  MESSAGEHOOK_ID = 1035360,
};


class MessageHook : public SceneHookData {
  public:
    MessageHook() : SceneHookData() { }
    virtual ~MessageHook() { }
    static NodeData* Alloc() { return NewObjClear(MessageHook); }
    virtual Bool Message(GeListNode* node, Int32 msg, void* pdata) override;
};


Bool MessageHook::Message(GeListNode* node, Int32 msg, void* pdata) {
  switch (msg) {
    case MSG_DOCUMENTINFO:
    case MSG_MULTI_RENDERNOTIFICATION:
      // TODO: Maybe we should instead wrap it in our own message data.
      GePluginMessage(msg, pdata);
      return true;
  }
  return SceneHookData::Message(node, msg, pdata);
}


Bool RegisterMessageSceneHook() {
  const Int32 flags = PLUGINFLAG_SCENEHOOK_NOTDRAGGABLE;
  const Int32 disklevel = 0;
  const Int32 priority = 0;
  return RegisterSceneHookPlugin(
    MESSAGEHOOK_ID, "c4ddev-messagehook", flags, MessageHook::Alloc,
    priority, disklevel, nullptr);
}
