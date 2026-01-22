# Seeded Hierarchy Action Scripts

EPMware provides pre-built (seeded) Logic Scripts that handle common hierarchy management scenarios. 

***Seeded Script : EW_SHARED_NODE_POSITION*** <br/>
This Logic Script is assigned to Essbase and Planning Applications automatically for all dimensions for the “Insert shared Member” action. The purpose of this Logic Script is to prevent the creation of a shared node before its Primary instance in the hierarchy.


## Next Steps

- [Post-Hierarchy Actions](../post-hierarchy-actions/index.md)
- [Creating Scripts](../../getting-started/creating-scripts.md)

---

!!! info "Note"
    Seeded scripts are designed to handle common scenarios. For specific business requirements, clone and customize rather than modifying the originals. This ensures upgrades don't override your customizations.