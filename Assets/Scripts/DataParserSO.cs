using UnityEngine;

public abstract class DataParserSO : ScriptableObject
{
    public abstract void HandleData(object data);
}