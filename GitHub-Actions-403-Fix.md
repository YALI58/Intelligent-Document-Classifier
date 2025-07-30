# GitHub Actions 403 权限错误解决方案

## 问题描述
GitHub Actions 返回 403 错误，表示权限不足。错误信息：
```
⚠️ GitHub release failed with status: 403
❌ Too many retries. Aborting...
```

## 解决方案

### 1. 检查仓库权限设置

#### 步骤1：进入仓库设置
1. 打开您的GitHub仓库
2. 点击 "Settings" 标签
3. 在左侧菜单中找到 "Actions" > "General"

#### 步骤2：配置权限
确保以下设置正确：

- ✅ **Workflow permissions**: 选择 "Read and write permissions"
- ✅ **Allow GitHub Actions to create and approve pull requests**: 勾选
- ✅ **Allow GitHub Actions to create and approve pull requests from outside collaborators**: 勾选

### 2. 检查仓库可见性

确保仓库不是私有仓库，或者如果是私有仓库，确保：
- 您有管理员权限
- GitHub Actions 有足够的权限访问仓库

### 3. 更新工作流文件

当前工作流文件使用官方GitHub Actions：

```yaml
permissions:
  contents: write
  actions: read

# 使用官方Actions
- name: Create Release
  uses: actions/create-release@v1
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

- name: Upload Release Asset
  uses: actions/upload-release-asset@v1
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 4. 手动创建Release（备用方案）

如果自动创建仍然失败，可以手动创建：

#### 方法1：GitHub网页界面
1. 进入仓库的 "Releases" 页面
2. 点击 "Create a new release"
3. 选择对应的标签版本
4. 填写标题和描述
5. 上传构建好的文件

#### 方法2：使用本地构建
```bash
# 本地构建可执行文件
python build_executable.py

# 手动上传到GitHub Releases
# 1. 进入GitHub仓库的Releases页面
# 2. 点击 "Create a new release"
# 3. 选择标签版本
# 4. 上传release目录中的文件
```

### 5. 检查GitHub Token

确保 `GITHUB_TOKEN` 有足够权限：

1. 进入仓库 Settings > Actions > General
2. 检查 "Workflow permissions" 设置
3. 确保选择了 "Read and write permissions"

### 6. 测试步骤

1. **推送测试标签**：
   ```bash
   git tag v1.1.1-test3
   git push origin v1.1.1-test3
   ```

2. **监控工作流**：
   - 在GitHub仓库的Actions标签页查看执行情况
   - 检查详细日志中的错误信息

3. **验证权限**：
   - 确保您有仓库的管理员权限
   - 检查仓库的可见性设置

### 7. 常见问题排查

| 问题 | 可能原因 | 解决方法 |
|------|----------|----------|
| 403 Forbidden | 权限不足 | 检查仓库权限设置 |
| Token无效 | Token过期 | 重新生成Token |
| 仓库私有 | 私有仓库限制 | 检查仓库可见性 |
| 网络问题 | 网络连接 | 重试或使用VPN |
| Action版本 | 版本过旧 | 使用最新版本的官方Actions |

### 8. 官方Actions的优势

使用官方GitHub Actions的优势：

- ✅ **稳定性高** - 由GitHub官方维护
- ✅ **兼容性好** - 与GitHub平台完美集成
- ✅ **权限明确** - 权限要求清晰
- ✅ **更新及时** - 定期更新和维护

### 9. 联系支持

如果问题持续存在：
1. 查看GitHub Actions的详细日志
2. 在GitHub Community中寻求帮助
3. 联系GitHub支持

---

**注意**：403错误通常是权限配置问题，按照上述步骤应该能够解决。使用官方GitHub Actions是最稳定可靠的方案。 