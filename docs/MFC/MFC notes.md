

# MFC随笔记录

随笔记录一些在上课时应用的MFC知识，以防止应用的时候会忘记。

有印象，需要时拿来能用就很好了。

工具选项RGB(206,235,206)会比较舒服一些。淡绿色的背景。





## 基础部分 

### 句柄与对象转换

#### HWND与CWnd对象之间的转换：

a)如果有CWnd对象如何获取这个对象内部的句柄？

```
pWnd ->m_hWnd
pWnd ->GetSafeHwnd();
CWnd wnd;
HWND h = wnd;
```

b)如果有句柄HWND如何转为CWnd?

```
static CWnd* CWnd::FromHandle(HWND hWnd);
```

- 注意：GetDlgItem内部都是靠FromHandle实现的。
- 注意：FromHandle内部是有Map禁止一个句柄被多个对象包含。
  就如同一个端口只能被一个进程占用，一个句柄只能有一个对象包含。
- 注意：FromHandle的返回值只限于本函数使用，不可以保存在成员变量长期使用。
  原因是不定期清理Map，参见：CWnd::DeleteTempMap

#### 句柄嫁接与子类化：

a)Attach和Detach就是单纯的嫁接与分离函数。
对象一旦嫁接入一个句柄，就可以自由地调用CWnd或其派生类的功能。
b)子类化Subclass内部包含Attach，额外再增加一个消息转拨到派生类（SubClass就是子类）
c)SubClassWindow函数内部核心功能就是Attach和::SetWindowLong
d)SubClassWindow必须与UnsubclassWindow()成对使用，如同Attach与Detach那样。
e)SubClassDlgItem是把2个函数合成一个函数：m_eye.SubclassDlgItem(IDC_SHOW, this);
m_eye.SubclassWindow(::GetDlgItem(m_hWnd, IDC_SHOW));
f)而且SubClassDlgItem不需要反子类化，可以不用调用UnsubclassWindow

#### 总结嫁接与子类化：

a)Attach和Detach就是单纯的嫁接
b)子类化Subclass内部包含Attach，增强了消息转移机制。
c)SubClassDlgItem简化了子类化功能，不需要反子类化UnsubclassWindow
d)类向导中建立关联变量的方法（内部就是子类化）

```
DDX_Control函数内的核心内容是，引用类成员变量m_xxx，
{
pDX->m_pDlgWnd->GetDlgItem(nIDC, &hWndCtrl);
rControl.SubclassWindow(hWndCtrl))

}
void CXxxxxx::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
	DDX_Control(pDX, IDC_LIST, m_list);
	DDX_Control(pDX, IDC_PRIOR, m_combo);
}
```

### 客户区拖动

使得在没有标题栏的时候可以拖动窗口，要利用`WM_NCHITTEST`。

### 定时器使用

一般是初始化函数设置定时器。

WM_TIMER消息映射函数中判断使用函数。

定时器间隔最小一般为10-15，吕大师测试的是16ms。

```c++
enum {STM_FLYMOVE = 888}
```

```c++
BOOL CMainDlg::OnInitDialog()
{
	CDialogEx::OnInitDialog();
	SetTimer(STM_FLYMOVE,16, NULL);//似乎最小值就是16
	return TRUE;  // 除非将焦点设置到控件，否则返回 TRUE
}
```

```c++
void CMainDlg::OnTimer(UINT_PTR nIDEvent)
{
	if (STM_FLYMOVE == nIDEvent)
	{
		m_pos.Offset(5*m_x, 5*m_y);//这实现的是函数调转偏移操作
		Invalidate(FALSE);
	}
	CDialogEx::OnTimer(nIDEvent);
}
```

### 获取屏幕宽高

全屏幕窗口

```
int cx = GetSystemMetrics(SM_CXSCREEN);
int cy = GetSystemMetrics(SM_CYSCREEN);
SetWindowPos(NULL, 0, 0, cx, cy, SWP_NOZORDER);
```

### 坐标转换

#### 获取控件相对客户区的坐标

```
CRect rc;//获取控件相对客户区的坐标
m_ok.GetWindowRect(&rc);
ScreenToClient(&rc);//从屏幕坐标，转移至根据主窗口的坐标？
```

### 布局控件跟随对话框变化

需要在对话框中，控件的属性调整，属性>动态布局，有两个选项：

- 调整大小类型，既是大小根据对话框的大小改变。
- 调整移动类型，既是位置根据对话框大小改变。

也可以自己用代码设置

计算m_cxMargin：

```
BOOL CAboutDlg::OnInitDialog()
{
	CDialogEx::OnInitDialog();
	CRect rect, rc;
	GetClientRect(&rect);
	m_ok.GetWindowRect(&rc);//这个是控件按钮的rect
	ScreenToClient(&rc);//应该是以对话框左上角为中心开始的一个矩形。
	m_cxMargin = rect.right-rc.right;
	m_cyMargin = rect.bottom-rc.bottom;
}
```

m_ok CButton控件根据size移动：

```
void CAboutDlg::OnSize(UINT nType, int cx, int cy)
{//m_ok CButton控件根据size移动。
	CDialogEx::OnSize(nType, cx, cy);
	if (m_ok)
	{//根据m_cxMargin平移
		CRect rc;
		m_ok.GetWindowRect(&rc);
		ScreenToClient(&rc);//从屏幕坐标，转移至根据主窗口的坐标？
		int x = cx - m_cxMargin - rc.right;
		int y = cy - m_cyMargin - rc.bottom;//平移的量
		rc.OffsetRect(x, y);
		m_ok.SetWindowPos(NULL, rc.left, rc.top, rc.Width(), rc.Height(), SWP_NOZORDER | SWP_NOSIZE);
	}
}
```

### Create创建控件的映射方法

**对于系统预设的控件，可以依照对话框自动生成的方法创建**

```
	afx_msg void OnMyButtonClick();//头文件中
```

```
	void CMainFrame::OnMyButtonClick()//cpp文件中
	{
	
	}
```

````
BEGIN_MESSAGE_MAP(CMainFrame, CFrameWnd)
	ON_BN_CLICKED(99, OnMyButtonClick)//99为Create时的ID
END_MESSAGE_MAP()
````

**对于自定义控件，可能需要用到自定义消息，并依据自定义消息建立映射**

### CImageList的使用

```
void CLeftView::InitCtrl()//可以创建该函数用于初始化CImageList以及其他的东西
{
	m_iList.Create(16, 16, ILC_COLOR32, 8, 8);//CImageList需要初始化才能使用

	m_tree.SetImageList(&m_iList, TVSIL_NORMAL);
	CString sFile;
	for (int i = 0; i < 6; i++)
	{
		sFile.Format(_T("./res/%d.ico"), i + 1);
		HICON hIcon =(HICON)LoadImage(AfxGetInstanceHandle(), sFile, IMAGE_ICON, 0, 0, LR_LOADFROMFILE);
		m_iList.Add(hIcon);
	}
	m_tree.SetImageList(&m_iList, TVSIL_NORMAL);//CImageList与m_tree绑定。
}
```

### CListCtrl单行满满选中

需要属性配合：

```
	m_list.ModifyStyle(0, LVS_REPORT LVS_SINGLESEL);//列表模式与单行选中
	m_list.SetExtendedStyle(LVS_EX_GRIDLINES | LVS_EX_FULLROWSELECT);//设置满行选中
```

这样配合NM_ClICK就可以实现一些复杂的功能。







## 六大GDI绘图对象

### `GetBitmapBits`函数

在视频软件开发室会用到改函数。视频流文件都形成bits，可以压缩再传输再set。  

该函数可以把加载的句柄`g_hBitmap`，在内存中形成一串代码。代码的长度和像素的个数有关，在内存中一般是`bmWidth * bmHeight * 4`，文件存储为了节省内存就是`bmWidth * bmHeight * 3`。

```
BITMAP bm;
GetObject(g_hBitmap, sizeof(bm), &bm);
int nCount = bm.bmWidth * bm.bmHeight * 4;
auto p = new char[nCount];
int n = GetBitmapBits(g_hBitmap, nCount, p);
delete[]p;
```

### 位图贴图流程

#### 位图显示：（win32）

（贴图技术）流程尽量背下来

1. 创建内存DC：

   HDC mdc = CreateCompatibleDC(hdc);

   //如果代入NULL代表：GetDC(NULL)桌面关联的DC

2. 内存DC选择位图：

   SelectObject(mdc, g_hBitmap);

3. 对窗口DC输出：

   BitBlt(hdc, 0, 0, 604, 603, mdc, 0, 0, SRCCOPY);

4. 删除内存DC

   DeleteDC(mdc);

 ```
   PAINTSTRUCT ps;//FILE 以前也是结构体，没必要去看内容。WSAStartup这些函数对应的结构体都没必要看。
   HDC hdc = BeginPaint(hWnd, &ps);
   HDC mdc = CreateCompatibleDC(hdc);//如果代入NULL代表：GetDC(NULL)桌面关联的DC
   SelectObject(mdc, g_hBitmap);
   BitBlt(hdc, 0, 0, 604, 603, mdc, 0, 0, SRCCOPY);
   DeleteDC(mdc);
   EndPaint(hWnd, &ps);
 ```

#### MFC下的位图显示流程：

```
CPaintDC dc(this); // 窗口DC
CDC mdc;
BITMAP bm;
m_bitmap.GetBitmap(&bm);
mdc.CreateCompatibleDC(&dc);
mdc.SelectObject(&m_bitmap);
dc.BitBlt(190, 120, bm.bmWidth/2, bm.bmHeight/2, &mdc, bm.bmWidth / 2, 	bm.bmHeight / 2, SRCCOPY);
```

#### BitBlt函数：

```
BOOL BitBlt(
  HDC   hdcDest,    // 目标设备上下文句柄
  int   nXDest,     // 目标矩形的左上角 x 坐标
  int   nYDest,     // 目标矩形的左上角 y 坐标
  int   nWidth,     // 矩形的宽度			    即图片的宽
  int   nHeight,    // 矩形的高度
  HDC   hdcSrc,     // 源设备上下文句柄
  int   nXSrc,      // 源矩形的左上角 x 坐标 		即图片的x
  int   nYSrc,      // 源矩形的左上角 y 坐标
  DWORD dwRop       // 光栅操作码
);
```

#### StretchBlt()拉伸贴图

在使用mdc.SelectObject(&dc)，可以使用dc调用StretchBlt函数来实现普通贴图、图片左右反转和上下翻转，以及放缩。

```
	//StrectchBlt放缩
	dc.StretchBlt(0, m_size.cy, m_size.cx*1.5, m_size.cy*1.5, &mdc, 20, 10, m_size.cx-100, m_size.cy-50, SRCCOPY);
	//StrectchBlt反转
	dc.StretchBlt(0, m_size.cy+ m_size.cy * 1.5, m_size.cx, m_size.cy, &mdc, m_size.cx, 0, -m_size.cx , m_size.cy, SRCCOPY);
	//反转中，是先定位起始点，然后取宽度
	//（猜测是从起始点开始，然后沿着宽度的矢量方向打印，倒头后，沿着高度矢量方向移动一格，继续打印。
	//所以这里参数的意思是，起点是（m_size.cx,0)即右上角。截取的长度矢量为（ -m_size.cx , m_size.cy）。
	//即x方向从内存中右至左选取像素点，在对话框中打印出来的是左右翻转。Y方向不变。
	
	dc.StretchBlt(m_size.cx * 1.5, 0, m_size.cx, m_size.cy, &mdc, m_size.cx - 100, 0, -m_size.cx+90, m_size.cy-100, SRCCOPY);
	//这里若矩形填充不完全，因为第8个参数是-m_size.cx-100，这里没有加括号,应该是-m_size.cx+100。参数填太多会选取一些背景色作为填充。

```

`pDC->CreateCompatibleDC(NULL);`参数可以是NULL



### 对话框背景后景色的刷新

```
case WM_ERASEBKGND://消息
		return TRUE;//默认返回 0，如果是非0那么就不会调用默认的刷新背景
		//MFC中 ， 你可以在OnEraseBkgnd函数中返回一个非零值
```

### 拖动客户区

在MFC中拖动客户区的方式只需要这个即可，此方法在Win32中不管用。

```
LRESULT CHitTestDlg::OnNcHitTest(CPoint point)
{//在WM_NCHITTEST的映射函数中返回HTCAPTION即可。
	return HTCAPTION;//return 别的就是别的功能
	return CDialogEx::OnNcHitTest(point);
}
```



### 空填充矩形

- 利用CreateBrushIndirect函数来调用BS_NULL属性实现真正的空填充。
- ​	dc.SelectStockObject(NULL_BURSH);

```c++
	//1.是空填充，但是繁琐。	
	CRect rc = { 0,0,m_size.cx,m_size.cy };
	CBrush brush;
	LOGBRUSH lb{ BS_NULL };
	brush.CreateBrushIndirect(&lb);

	//2.这个空填充方式比上一个好，一句搞定
	dc.SelectStockObject(NULL_BRUSH);

	CPen pen(PS_SOLID, 2, RGB(255, 255, 125));
	dc.SelectObject(&pen);
	dc.SelectObject(&brush);
	dc.Rectangle(&rc);
```



### CRgn使用示例 

#### 绘制一个圆形的图片

利用Rgn，选取一个圆形区域，利用圆形区域绘制一个图。

```c++
void CRgnDlg::OnPaint()
{
	CPaintDC dc(this); // 用于绘制的设备上下文
	CRect rc = { 0,0,m_size.cx,m_size.cy };
	rc.OffsetRect(50, 0);
	dc.FillSolidRect(CRect{ 0,0,800,800 }, RGB(0, 155, 125));
	
	//创建一个Rgn
	//CRgn用于表示和处理裁剪区域，裁剪区域是指一个图形区域，
	//它定义了一个矩形区域内可以绘制的图形区域，超出这个区域的绘制会被剪裁掉，不会显示在屏幕上。
	CRgn rgn;
	rgn.CreateEllipticRgn(rc.left, rc.top, rc.right, rc.bottom);

	dc.SelectObject(&rgn);
	dc.BitBlt(50, 0, m_size.cx, m_size.cy, &m_dc, 0, 0, SRCCOPY);
	
	dc.SelectClipRgn(NULL); // 恢复原始裁剪区域
}
```

#### 绘制一个自定义的窗口

利用Rgn，选取绘制范围，利用`SetWindowRgn`绘制一个自定义的窗口

```c++
void CRgnDlg::OnPaint()
{
	CPaintDC dc(this); // 用于绘制的设备上下文
	CRect rc = { 0,0,m_size.cx,m_size.cy };//图片尺寸

	CRgn rgn;//图片的Rgn
	rgn.CreateEllipticRgn(rc.left, rc.top, rc.right, rc.bottom);

	dc.SelectObject(&rgn);
	dc.BitBlt(0, 0, m_size.cx, m_size.cy, &m_dc, 0, 0, SRCCOPY);

	CRgn r;//窗口的Rgn
	r.CreateRectRgn(50, 50, 500, 500);
	SetWindowRgn(r, FALSE);
	//在SetWindowRgn后，只是绘制选中区域的Rgn，其他部分不绘制，但是坐标没有变化。
	//比如示例中，重绘后的小矩形窗口，左上角坐标为50,50。
	dc.SelectClipRgn(NULL); // 恢复原始裁剪区域
}
```

#### Rgn合并

利用`CombineRgn(&r, &r1, RGN_COPY);`可以实现Rgn的挖去与重叠，交集、并集等。

- RGN_AND 使用复盖率区域两个区域(型交叉处）。
- RGN_COPY 创建区域1的副本(由 pRgn1）。

- RGN_DIFF 创建包含不属于区域2的区域区域1的区域(由 pRgn1) (由 pRgn2）。

- RGN_OR 全文合并两个区域(联合）。

- RGN_XOR 合并两个区域，但取消复盖率区域

```c++
void CRGN类简介Dlg::OnPaint()
{
	CPaintDC dc(this); // 用于绘制的设备上下文
	CRgn r, r1;
	POINT pts[] = { {334,120},{596,345},{497,529},{217,517},
	{118,406},{319,319} };
	r.CreateEllipticRgn(30, 30, 500, 400);
	r1.CreatePolygonRgn(pts,_countof(pts), ALTERNATE);
	//这个ALTERANTE加载模式不知道有什么区别。
	r.CombineRgn(&r, &r1, RGN_COPY);
//	RGN_XOR 共同部分挖掉
	dc.SelectObject(r);
	dc.BitBlt(0, 0, m_size.cx, m_size.cy, &m_dc, 0, 0, SRCCOPY);
}
```

#### Rgn恢复到默认

因为`int SelectObject(CRgn rgn)`没有返回旧的对象，所以不能用记录旧RGN的方式返回。

可以使用Bitmap来回复旧Rgn。

```
	BITMAP bm;
	dc.GetCurrentBitmap()->GetBitmap(&bm);
	//这个bm的尺寸就是旧Bitmap画布的尺寸。
	r.DeleteObject();
	r.CreateRectRgn(0, 0, bm.bmWidth, bm.bmHeight);
	//把rgn恢复到默认。因为dc没有SelectBitmap，所以默认的CurrentBitmap就是画布原本的大小。
	dc.SelectObject(&r);
```

#### GetRgnBox

GetRgnBox可以获得最小收束的矩形。

GetRegionData可以获得

```
    CRect rect;
    r.GetRgnBox(rect);
    
    int nCount = r.GetRegionData(NULL, 0) ;
    //带入NULL返回值包含对区域数据需要字节数，有点像字节转换那里
    auto p = new char[nCount];
    LPRGNDATA pData = (LPRGNDATA)p;
    int n = r.GetRegionData(pData, nCount);
    sizeof(RGNDATA);
    //一般与CreateFromData一起使用，但是我不会。
```



### 内存DC不能绘制

内存DC不能绘制问题的解决。内存DC绘制的探究。

正常情况下，不能绘制要考虑到是不是矩形的面积小于等于0导致不能绘制，或者绘制的位置超过了显示的范围。

在这里是内存DC没有SelectObject导致的。因为没有Select，默认的CBitmap大小又只有1，所以不能成功的绘制出图片。

```c++
void C内存DC探究Dlg::OnPaint()
{
	CPaintDC dc(this); // 用于绘制的设备上下文

	CDC mdc;
	mdc.CreateCompatibleDC(NULL);

	BITMAP bm;
	auto pBitmap = mdc.GetCurrentBitmap();
	pBitmap->GetBitmap(&bm);
	//由上面的语句可以知道，内存DC默认的Bitmap画布只有一个字节，一个像素，所以dc.BitBlt没有作用。
	pBitmap = dc.GetCurrentBitmap();
	pBitmap->GetBitmap(&bm);
	//CPaintDC 默认的Bitmap大小与 WindowRect大小一样(宽高一样）。

	CBitmap bmp;
	bmp.CreateCompatibleBitmap(&dc, 300, 300);
    //新创建的位图将与这个设备dc上下文兼容。这意味着位图的特性将与指定设备上下文匹配，
	//包括位图的位深度、颜色表等。 
	mdc.SelectObject(&bmp);
	//在创建了DC并选择后，就可以绘制出图案了，不过默认的CBitmap往往是32位，数值为0x00000000。
	dc.FillSolidRect(CRect{ 0,0,200,200 }, RGB(255, 255, 125));
	dc.BitBlt(10, 10, 300, 300, &mdc, 0, 0, SRCCOPY);
}
```

### Bitmap透明

透明的方法:

- MakeRgn和SelectObject(Rgn)
- 自己通过算法封装透明方法：参见CMemoryDC类。
- CDC::TransparentBlt或者同名API。
- CImage类（CImage::TransparentBlt）

#### MakeRgn

利用GetPixel(j, i)，判断像素等不等于背景，若不能，则用RGN_OR进行Rgn合并。

注意的是rResource.CreateRectRgn(0, 0, 0, 0)；的rgn区域为0，1个像素是（0,0,1,1）。

```c++
void MakeRgn(CRgn& rResource, COLORREF col)
{//利用MakeRgn逐个像素检查合并，形成一个没有背景色的Rgn区域。
    if(!rResource.GetSafeHandle())
        rResource.CreateRectRgn(0, 0, 0, 0);
    for (int i = 0; i < m_size.cy; ++i)
    {
        for (int j = 0; j < m_size.cx; ++j)
        {
            if (GetPixel(j, i) != col)
            {
                CRgn rTemp;
                rTemp.CreateRectRgn(j, i, j + 1, i + 1);//1x1 像素,这里的ij有一点颠倒
                rResource.CombineRgn(&rResource, &rTemp, RGN_OR);
            }
        }
    }
}
```

#### CDC::TransparentBlt

据说老版本可能不太好用，但最新的VS MFC 中很好用。

```
BOOL TransparentBlt(
   int xDest,
   int yDest,
   int nDestWidth,
   int nDestHeight,
   CDC* pSrcDC,
   int xSrc,
   int ySrc,
   int nSrcWidth,
   int nSrcHeight,
   UINT clrTransparent //在将的源位图的RGB颜色透明
);//类似StretchBlt。
```



#### 封装BitTrans

来自吕大师的代码

OnPaint中，pDC带入dc，因为内部用dc调用BitBlt。

BitTrans：

```
void BitTrans(
		int nXDest,		// 目标起点X
		int nYDest,		// 目标起点Y
		int nWidthDest,	// 目标宽度
		int nHeightDest,// 目标高度
		CDC* pDC,		// 目标DC
		int nXSrc,		// 来源起点X
		int nYSrc,		// 来源起点Y
		COLORREF crTrans// 透明色
	)
	{
		CMemoryDC dcImage(nWidthDest, nHeightDest, pDC);//临时DC
		CBitmap bmpMask;
		bmpMask.CreateBitmap(nWidthDest, nHeightDest, 1, 1, NULL);            // 创建单色掩码位图
		CDC dcMask;//掩码DC 
		dcMask.CreateCompatibleDC(pDC);
		dcMask.SelectObject(bmpMask);
		//将载入位图的内存DC中的位图，拷贝到临时DC中
		dcImage.BitBlt(0, 0, nWidthDest, nHeightDest, this, nXSrc, nYSrc, SRCCOPY);

		// 设置临时DC的透明色
		dcImage.SetBkColor(crTrans);
		//掩码DC的透明区域为白色其它区域为黑色
		dcMask.BitBlt(0, 0, nWidthDest, nHeightDest, &dcImage, 0, 0, SRCCOPY);

		//临时DC透明区域为黑色，其它区域保持不变
		dcImage.SetBkColor(RGB(0, 0, 0));
		dcImage.SetTextColor(RGB(255, 255, 255));
		dcImage.BitBlt(0, 0, nWidthDest, nHeightDest, &dcMask, 0, 0, SRCAND);

		// 目标DC透明部分保持屏幕不变，其它部分变成黑色
		pDC->SetBkColor(RGB(255, 255, 255));
		pDC->SetTextColor(RGB(0, 0, 0));
		pDC->BitBlt(nXDest, nYDest, nWidthDest, nHeightDest, &dcMask, 0, 0, SRCAND);
		pDC->BitBlt(nXDest, nYDest, nWidthDest, nHeightDest, &dcImage, 0, 0, SRCPAINT);
	}
```

#### 封装StretchTrans

```
void StretchTrans(
		int nXDest,			// 目标起点X
		int nYDest,			// 目标起点Y
		int nWidthDest,     // 目标宽度
		int nHeightDest,    // 目标高度
		CDC* pDC,			// 目标DC
		int nXSrc,			// 来源起点X
		int nYSrc,			// 来源起点Y
		int nWidthSrc,		// 来源宽度
		int nHeightSrc,		// 来源高度
		COLORREF crTrans	// 透明色
	)
	{
		CMemoryDC dcImage(nWidthDest, nHeightDest, pDC);//临时DC
		CBitmap bmpMask;
		// 创建单色掩码位图
		bmpMask.CreateBitmap(nWidthDest, nHeightDest, 1, 1, NULL);
		CDC dcMask;
		dcMask.CreateCompatibleDC(pDC);
		dcMask.SelectObject(bmpMask);

		// 将载入位图的内存DC中的位图，拷贝到临时DC中
		if (nWidthDest == nWidthSrc && nHeightDest == nHeightSrc)
			dcImage.BitBlt(0, 0, nWidthDest, nHeightDest, this, nXSrc, nYSrc, SRCCOPY);
		else
			dcImage.StretchBlt(0, 0, nWidthDest, nHeightDest,
				this, nXSrc, nYSrc, nWidthSrc, nHeightSrc, SRCCOPY);

		// 设置临时DC的透明色
		dcImage.SetBkColor(crTrans);
		//掩码DC的透明区域为白色其它区域为黑色
		dcMask.BitBlt(0, 0, nWidthDest, nHeightDest, &dcImage, 0, 0, SRCCOPY);

		//临时DC透明区域为黑色，其它区域保持不变
		dcImage.SetBkColor(RGB(0, 0, 0));
		dcImage.SetTextColor(RGB(255, 255, 255));
		dcImage.BitBlt(0, 0, nWidthDest, nHeightDest, &dcMask, 0, 0, SRCAND);

		// 目标DC透明部分保持屏幕不变，其它部分变成黑色
		pDC->SetBkColor(RGB(255, 255, 255));
		pDC->SetTextColor(RGB(0, 0, 0));
		pDC->BitBlt(nXDest, nYDest, nWidthDest, nHeightDest, &dcMask, 0, 0, SRCAND);
		pDC->BitBlt(nXDest, nYDest, nWidthDest, nHeightDest, &dcImage, 0, 0, SRCPAINT);
	}
```

### 双缓冲机制应对频闪 

OnPaint绘图会发生闪烁，而且贴图越多，闪烁越频繁，单张贴图不闪。这是贴图交替输出造成的。

这里需要用到双缓冲机制，核心是：把贴图先贴到内存上，再由dc输出内存dc就好了。只贴一次。

m_dc的尺寸是变动的。

理论上都要做双缓冲，面积太小没啥影响可以不做双缓冲。

#### 不考虑背景色

即`Invalidate(FALSE);`不刷新背景。

m_dc要随着尺寸变化，并且也需要初始化：

```
void Clvxin31Dlg::OnSize(UINT nType, int cx, int cy)
{
	CDialogEx::OnSize(nType, cx, cy);
	m_dc.DeleteDC();
	m_dc.Create(cx, cy);
}
```

m_dc在类中定义，核心算法

```
void CMainDlg::OnPaint()
{
	CPaintDC dc(this); // 用于绘制的设备上下文
	CRect rect;
	GetWindowRect(&rect);
	m_dc.SetStretchBltMode(STRETCH_HALFTONE);
	m_dc.StretchBlt(0, 0, rect.Width(), rect.Height(), &m_dcBack,
		0, 0, m_dcBack.GetWidth(), m_dcBack.GetHeight(), SRCCOPY);
	CMemoryDC mdc;
	mdc.Create(300, 300);
	m_dc.BitBlt(300, 300, 300, 300, &mdc, 0, 0, SRCCOPY);
	
	CRect rectClient;
	GetClientRect(&rectClient);
//根据链表动态打印蝴蝶。
	auto pos = m_list.GetHeadPosition();
	while (pos)
	{
		Flys& data = m_list.GetNext(pos);
		//这里需要加引用。
		data.m_pos.Offset(data.m_dir);
		//蝴蝶碰到边缘反弹回来
		if (data.m_pos.x<rectClient.left || data.m_pos.x + m_dcFlys->GetWidth()>rectClient.right)
			data.m_dir.x *= -1;
		if (data.m_pos.y<rectClient.top || data.m_pos.y + m_dcFlys->GetHeight()>rectClient.bottom)
			data.m_dir.y *= -1;
		//蝴蝶的贴图。
		m_dc.TransparentBlt(data.m_pos.x, data.m_pos.y, m_dcFlys->GetWidth(), m_dcFlys->GetHeight(),
			&m_dcFlys[data.m_nFlyIndex], 0, 0, m_dcFlys->GetWidth(), m_dcFlys->GetHeight(), RGB(255, 0, 255));
		if (++data.m_nFlyIndex >= _countof(m_dcFlys))
			data.m_nFlyIndex = 0;
	}
	所有都输入到m_dc后，只用dc打印一次m_dc即可。
	dc.BitBlt(0, 0, m_dc.GetWidth(), m_dc.GetHeight(), &m_dc, 0, 0, SRCCOPY);
}
```

#### 考虑背景色

两种解决方案：

1. 使用`Invalidate(FALSE);`，带入FALSE而不是TRUE，可以免刷新背景造成的重复刷新闪烁。
2. 在WM_ERASEBKGND的映射函数中return TRUE，使背景色刷新失效。如果要使用背景，可以在OnPaint中伪造背景。







## 框架视图





### 注册窗口类

classname注册窗口类型名：有3种方式注册

- 原始API：`ATOM RegisterClass(const WNDCLASS *lpWndClass);`
- MFC封装之后叫做`AfxRegisterClass`，类似于`AfxMessageBox`封装了`MessageBox(API)`
- MFC再次封装了一个真正的简易注册函数叫做：`AfxRegisterWndClass`
  返回值是自动生成字符串，字符串的内容包括三要素的句柄sprintf生成的文字：

`AfxRegisterWndClass`因为框架只需要框架，视图会覆盖框架，并实现视图的功能，所以一般都默认用简易注册。

类名为HCursor等句柄sprintf后形成的一长串数字。以之前的CLadderCtrl为例，需要在Create函数中操作。

自定义窗口类都可以搞一搞。

```
BOOL CLadderCtrl::Create(DWORD dwStyle, const RECT& rect, CWnd* pParentWnd, UINT nID)
{
	if (!IsRegistered(_T("王八蛋")))//应该是可以防止重复创建窗口类？
	{//WNDCLASS结构体创建与赋值
		WNDCLASS wc = { CS_HREDRAW | CS_VREDRAW };//左右上下拉伸刷新
		wc.hCursor = theApp.LoadStandardCursor(IDC_HAND);
		wc.hbrBackground = m_brBk;
		wc.lpfnWndProc = ::DefWindowProc;
		wc.lpszClassName = _T("王八蛋");
		RegisterClass(&wc);//为什么Create(_T("Edit")
	}
    return this->CWnd::Create(_T("王八蛋"), NULL, dwStyle, rect, pParentWnd, nID);
    //记得Create函数中添加新注册的类名。
}
```

```
inline static bool IsRegistered(LPCTSTR sClass)
{//可用这个函数判断
    WNDCLASSEX wcex;
    return (GetClassInfoEx(NULL, sClass, &wcex) != 0);
}
```



```c++
LPCTSTR  AfxRegisterWndClass( 
   UINT nClassStyle, 
   HCURSOR hCursor = 0, 
   HBRUSH hbrBackground = 0, 
   HICON hIcon = 0  
);
```

```c++
附录：AfxRegisterClass比API就是多了GetClassInfo探测一下是否已注册过了。
BOOL AFXAPI AfxRegisterClass(WNDCLASS* lpWndClass)
{
	WNDCLASS wndcls;
	if (GetClassInfo(lpWndClass->hInstance, lpWndClass->lpszClassName,
		&wndcls))
	{// class already registered
		return TRUE;
	}
	if (!RegisterClass(lpWndClass))
	{
		TRACE(traceAppMsg, 0, _T("Can't register window class named %Ts\n"),
			lpWndClass->lpszClassName);
		return FALSE;
	}
}
```



### MFC环境下创建框架窗口的必备条件

- InitInstance必须return TRUE;
- theApp.m_pMainWnd 必须指向主窗口对象地址：
- 主窗口对象必须是堆空间或者生命期足够。

因为Frame是非阻塞，必须返回TRUE。

### 关于注册时的要素与窗口设置

- 例如：注册时你指定灰色背景，窗口生成后可以在WM_ERASEBKGND消息中改成别的颜色。
- 其他包括图标（SetIcon），光标WM_SETCURSOR消息中改，以及菜单（SetMenu）。
- 例如：但凡Create一个Edit注册时的要素都会默认呈现，比如光标的形状，背景是白色。
- 但是后面都是可以改的，比如你想把某个edit改为绿底红字的。（WM_CTLCOLOR）

**修改的位置**

- 在InitInstance()中进行修改，Create后，利用SetMenu或者SetIcon等进行修改。

- 注册时，在PreCreateWindow中修改cs结构体的信息。
- 在创建后，利用消息WM_SETCURSOR或者其他位置进行修改。

### 对话框CDialog类不偏爱WM_CREATE消息

a)对话框类使用WM_INITDIALOG消息或者虚函数来初始化；

WM_CREATE消息对于对话框也是有效的对话框程序需要初始化控件，WM_CREATE是主窗口刚刚创建好，控件还没有。所以它偏爱OnInitDialog虚函数，控件都被创建好之后方便初始化那些控件。

### CFrameWnd类简介

- CFrameWnd类所有的内部窗口都是代码创建的。而不像对话框是拖入的。所以常在WM_CREATE中初始化
- CFrameWnd::rectDefault管理层叠static const CRect rectDefault;
- LoadFrame内部包含CreateFrame，同时执行注册以及加载快捷键等

### PreCreateWindow

创建窗口的预处理函数：`virtual BOOL PreCreateWindow(CREATESTRUCT& cs);`

在这里Create函数前，会进行窗口注册，所以LoadFrame与Create函数都可以不经函数前注册创建窗口。

注册的结构体规格包括光标，图标以及背景颜色等；以及位置、高宽以及菜单，style和dwExStyle。

cs结构体修改后，例如修改了cs.hMenu（）后，经过注册也可以启用(可能是AfxRegisterWndClass(0)中调用了cs结构体。

为什么LoadFrame中使用注册，而CreateFrame根本没注册都好使？
那就是因为窗口预处理中执行注册，可以说即使从CWnd类派生你只要做预处理就不用RegisterClass。

### 从CListView派生时出错

类似从视图控件派生提示未定义的类，需要考虑是否包含了头文件`afxcview.h`。

#### TOOLBar或者菜单的按钮不亮

可能是需要添加到类中

- 在类视图中搜索菜单按钮或者bar按钮的ID，如`ID_EDIT_INPUT`然后添加到类中建立映射。
- Menu按钮ID可以与ToolBar控件ID一样，这样可以用一个映射同时起作用。
- 如果ToolBar不亮，点一下List窗口就会亮了

### 消息传递机制

在CMainFrame中，OnCmdMsg函数内，可以进行消息派发。

例如我同样用ID_EDIT_INPUT，但是该id可以形成多处消息映射，可以在CMainView中映射为函数，也可以在CMainFrame中当做函数。所以这时候需要消息机制来进行派发。默认是主框架处理，没有就在其他地方处理。

如果内部添加派发语句，则有限处理其他处的派发。

如果return FALSE，那么菜单按钮和ToolBar按钮会变成灰色，很严重。

```
BOOL CMainFrame::OnCmdMsg(UINT nID, int nCode, void* pExtra, AFX_CMDHANDLERINFO* pHandlerInfo)
{//m_pMainView是一个CView类型的指针，可以指向子类封装的函数，不知可不可以。
	if(m_pMainView&&m_pMainView->OnCmdMsg(nID,nCode,pExtra,pHandlerInfo))
		return TRUE;//表示成功处理，return FALSE 干脆就不刷新了。
	// 否则，执行默认处理
	return CFrameWnd::OnCmdMsg(nID, nCode, pExtra, pHandlerInfo);
}
```

### CHtmlView

这个ie内核，感觉没啥大用，现在谁用着玩意开发网页啊。随便看看就行。

### 视图分割CSplitterWnd m_split;

在使用多个视图时，可以用	`CSplitterWnd m_split`分割。

```
	CSplitterWnd m_split;//头文件中
```

```
	m_split.CreateStatic(this, 1, 2);//分出来的句柄必须填满，有空的就会触发断言
	m_split.CreateView(0, 0, RUNTIME_CLASS(CLeftView), {150,0}, NULL);
	//宽度是150，没有阻挡则延长到边缘，比如此处没有指定上下，所以就是上下通顶。
	m_split.CreateView(0, 1, RUNTIME_CLASS(CRightView), { 150,0 }, NULL);
	theApp.m_pLeftView = (CLeftView*)m_split.GetPane(0, 0);
	theApp.m_pRightView = (CRightView*)m_split.GetPane(0, 0);
	//m_pRightView 也可在各自的构造函数中赋值。
	//放在CApp中，可以实现灵活调用
```

#### CListCtrl与CListView的创建原理：

a)CListCtrl的内部创建原理是通过CWnd::Create(sClassName,....)来实现的。
b)CStatic,CEdit,CButton的内部创建原理无一不是这个原理，即使是拖入对话框的控件底层也是这样实现的。
（通过.rc读取风格和位置等要素，再调用CWnd类的Create函数）
c)CListView和CTreeView整个类都几乎没有代码，其实就是一个变种的CListCtrl或者CTreeCtrl。
d)所以你会看到直接强转：

```
INLINE CListCtrl& CListView::GetListCtrl() const
	{ return *(CListCtrl*)this; }
```

#### Split创建视图、删除视图

分割是做大软件必不可少的一项技术。

```
theApp.m_split.CreateView(0, 1, RUNTIME_CLASS(CHomeView), { 150,0 }, NULL); //创建
split.DeleteView(0, 1);//释放
split.RecalcLayout();//刷新
```

**如果分隔栏太丑**

可以用派生类派生CSplitterWnd，然后再OnPaint中重写OnPaint函数进行绘制。



### Delete造成的问题

```
theApp.m_split.DeleteView(0, 1);
theApp.m_split.CreateView(0, 1, RUNTIME_CLASS(CRightView), { 0,0 }, NULL);
theApp.m_pRightView = (CRightView*)theApp.m_split.GetPane(0, 1);
//这个语法并不安全，以为在delete与theApp.m_pRightView被赋值的期间，该指针处于野指针状态，如果为空，则会出现错误。
```

所以在下方的处理中造成了问题，`改用IsWindow(theApp.m_pRightView->GetSafeHwnd())`判断可以解决野指针造成的问题。

```
BOOL CMainFrame::OnCmdMsg(UINT nID, int nCode, void* pExtra, AFX_CMDHANDLERINFO* pHandlerInfo)
{
	if (IsWindow(theApp.m_pRightView->GetSafeHwnd()) && theApp.m_pRightView->OnCmdMsg(nID, nCode, pExtra, pHandlerInfo))
		return TRUE;

	// 否则，执行默认处理
	return CFrameWnd::OnCmdMsg(nID, nCode, pExtra, pHandlerInfo);
}
```

### ToolBar的使用方法

1、高级工具栏的开发
a)文字工具栏开发：调用CToolBar::SetButtonText和CBoolBar::SetSizes方法；
b)工具箱创建时要指定：CBRS_SIZE_FIXED
调用CToolBar::SetButtonStyle方法，为n个按钮一行做分行属性。

#### 给CToolBar添加文字

还有CToolBar停靠在窗口的右侧

```
void CMainFrame::InitTools()
{
	LPCTSTR st[] = {
		_T("新建"),_T("打开"),_T("保存"),_T(""),_T("剪切"),_T("拷贝"),_T("粘贴"),_T(""),_T("打印"),_T("帮助")
	};
	int nCount = m_wndToolBar.GetCount();
	for (int i = 0; i < nCount; ++i)
	{
		m_wndToolBar.SetButtonText(i, st[i]);
	}
	CRect rect;
	m_wndToolBar.GetItemRect(0, rect);//加文字以后rect变大，如果不SetSizes，文字不会显示
	m_wndToolBar.SetSizes(rect.Size(), { 16,15 });
	GetWindowRect(&rect);

	//toolBox 的悬浮与分割，停靠在窗口的右侧，需要CBRS_SIZE_FIXED属性支持
	m_toolBox.SetButtonStyle(1, TBBS_BUTTON | TBBS_WRAPPED);
	m_toolBox.SetButtonStyle(3, TBBS_BUTTON | TBBS_WRAPPED);
	m_toolBox.SetButtonStyle(5, TBBS_BUTTON | TBBS_WRAPPED);
	m_toolBox.SetButtonStyle(7, TBBS_BUTTON | TBBS_WRAPPED);//需要配合FIXED属性
	FloatControlBar(&m_toolBox, { rect.right - 80,rect.top + 100 });
}
```







## 类介绍

### CGdi类

#### CGfiObject

GDI绘图类共同的基类

```
typedef void * HGDIOBJ;
class CGdiObject : public CObject
{
public:
// Attributes
	HGDIOBJ m_hObject;     // 用来存储：HPEN HBRUSH HFONT HBITMAP ...
	operator HGDIOBJ() const;
	HGDIOBJ GetSafeHandle() const;
	static CGdiObject* PASCAL FromHandle(HGDIOBJ hObject);
	static void PASCAL DeleteTempMap();  //有点像那个CWnd，也有这个缓存图。这个是清除
	BOOL Attach(HGDIOBJ hObject);   //这个是利用句柄生成
	HGDIOBJ Detach();
// Constructors
	CGdiObject(); // must Create a derived class object
	BOOL DeleteObject();//内部就是API DeleteObject

	UINT GetObjectType() const;
**	BOOL CreateStockObject(int nIndex);//内部是：m_hObject=GetStockObject;
	//这个有点意思，可以输入NULL_BRUSH查看内部默认的那些东西
};

```



#### CBitmap类

```
class CBitmap : public CGdiObject
{
	DECLARE_DYNAMIC(CBitmap)
public:
	static CBitmap* PASCAL FromHandle(HBITMAP hBitmap);//生成外壳类
// Constructors
	CBitmap();
	BOOL LoadBitmap(LPCTSTR lpszResourceName);
	BOOL LoadBitmap(UINT nIDResource);//加载位图
**	BOOL LoadOEMBitmap(UINT nIDBitmap); // for OBM_/OCR_/OIC_
//这个函数可以加载一些系统的图，包括打钩恢复任务啥的都有。
	BOOL LoadMappedBitmap(UINT nIDBitmap, UINT nFlags = 0,
		LPCOLORMAP lpColorMap = NULL, int nMapSize = 0);
	BOOL CreateBitmap(int nWidth, int nHeight, UINT nPlanes, UINT nBitcount,
			const void* lpBits);
	BOOL CreateBitmapIndirect(LPBITMAP lpBitmap);//根据详细信息创建位图
	BOOL CreateCompatibleBitmap(CDC* pDC, int nWidth, int nHeight);//创建兼容位图
	BOOL CreateDiscardableBitmap(CDC* pDC, int nWidth, int nHeight);
// Attributes
	operator HBITMAP() const;
	int GetBitmap(BITMAP* pBitMap);
// Operations
	DWORD SetBitmapBits(DWORD dwCount, const void* lpBits);
	DWORD GetBitmapBits(DWORD dwCount, LPVOID lpBits) const;
	CSize SetBitmapDimension(int nWidth, int nHeight);
	CSize GetBitmapDimension() const;
// Implementation
public:
	virtual ~CBitmap();
#ifdef _DEBUG
	virtual void Dump(CDumpContext& dc) const;
#endif
};
```



##### CBitmap::CreateBitmap

利用CreateBitmap函数创建CBitmap：

```
void CTestDlg::OnPaint()
{
	CPaintDC dc(this); // 用于绘制的设备上下文
	BITMAP bm;
	m_bitmap.GetBitmap(&bm);
	int n = bm.bmHeight*bm.bmWidthBytes;//获取图片的字节数
	void* pBits = new char[n];
	m_bitmap.GetBitmapBits(n,pBits);
	CBitmap bmp;
	bmp.CreateBitmap(bm.bmWidth, bm.bmHeight-300, 1, 32, pBits);
	//以上为生成图片的步骤，注意的是，图片的打印应该是从左至右，从上至下打印的，原图宽为595，高548,
	//所以如果bm.bmWidth如果不是正好等于原图宽，就会打印出很奇怪的图片，差的越多，偏的越大。
	//bm.Height的值相对影响就不是很大。
	
	//如果用CreateBitmapIndirect构造，则会开辟一块与原图片相同大小的空间，里面的颜色都是黑色。
	bmp.CreateBitmapIndirect(&bm);
	bmp.SetBitmapBits(n, pBits);//把黑色空间填充色彩，n为字节数。
	//如果减去bm.bmWidthBytes，则少打印一行
	CDC mdc;
	mdc.CreateCompatibleDC(&dc);
	mdc.SelectObject(&bmp);
	//贴图
	dc.BitBlt(0, 0, bm.bmWidth, bm.bmHeight, &mdc, 0, 0, SRCCOPY);
}
```

#### CRgn类

```c++
class CRgn : public CGdiObject
{
public:
	static CRgn* PASCAL FromHandle(HRGN hRgn);
	operator HRGN() const;

// 封装的特点是没有使用Overload重载函数，结构体就是XXXIndirect
	CRgn();
//创建矩形区域
	BOOL CreateRectRgn(int x1, int y1, int x2, int y2);
	BOOL CreateRectRgnIndirect(LPCRECT lpRect);
//创建圆形区域
	BOOL CreateEllipticRgn(int x1, int y1, int x2, int y2);
	BOOL CreateEllipticRgnIndirect(LPCRECT lpRect);
//多边形
	BOOL CreatePolygonRgn(LPPOINT lpPoints, int nCount, int nMode);
	BOOL CreatePolyPolygonRgn(LPPOINT lpPoints, LPINT lpPolyCounts,
			int nCount, int nPolyFillMode);
//圆角矩形
	BOOL CreateRoundRectRgn(int x1, int y1, int x2, int y2, int x3, int y3);
//
	BOOL CreateFromPath(CDC* pDC);
	BOOL CreateFromData(const XFORM* lpXForm, int nCount,
		const RGNDATA* pRgnData);

// 修改矩形
	void SetRectRgn(int x1, int y1, int x2, int y2);
	void SetRectRgn(LPCRECT lpRect);
//混合
	int CombineRgn(const CRgn* pRgn1, const CRgn* pRgn2, int nCombineMode);
	int CopyRgn(const CRgn* pRgnSrc);
//判断区域完全一样
	BOOL EqualRgn(const CRgn* pRgn) const;
//判断一个点是否在区域内
	BOOL PtInRegion(int x, int y) const;
	BOOL PtInRegion(POINT point) const;
//保持形状不变偏移
	int OffsetRgn(int x, int y);
	int OffsetRgn(POINT point);
//框图
	int GetRgnBox(LPRECT lpRect) const;
	
	BOOL RectInRegion(LPCRECT lpRect) const;
	int GetRegionData(LPRGNDATA lpRgnData, int nCount) const;

// Implementation
	virtual ~CRgn();
};
```



### 框架视图

#### CFrameWnd类 

与CDialog一样继承自Dialog但是也有些许的不同

**CFrameWnd与CDialog类初始化**

- CDialog类使用WM_INITDIALOG消息或者虚函数来初始化，WM_CREATE消息对于对话框也有效的，为什么对话框很这个消息？对话框程序需要初始化控件，WM_CREATE是主窗口刚刚创建好，控件还没有。所以它偏爱OnInitDialog虚函数，控件都被创建好之后方便初始化那些控件。
- CFrameWnd类偏爱WM_CREATE，因为所有的内部窗口都是代码创建的。
  而不像对话框是拖入的。CFrameWnd::rectDefault管理层叠static const CRect rectDefault;LoadFrame内部包含CreateFrame，同时执行注册以及加载快捷键等（参见附录）

```
class CFrameWnd : public CWnd
{
	DECLARE_DYNCREATE(CFrameWnd)
// Constructors
public:
	static AFX_DATA const CRect rectDefault;
	CFrameWnd();
	BOOL LoadAccelTable(LPCTSTR lpszResourceName);
//创建框架   这个Create内部不会注册 下面的LoadFrame会注册
	virtual BOOL Create(LPCTSTR lpszClassName,
				LPCTSTR lpszWindowName,
				DWORD dwStyle = WS_OVERLAPPEDWINDOW,
				const RECT& rect = rectDefault,
				CWnd* pParentWnd = NULL,        // != NULL for popups
				LPCTSTR lpszMenuName = NULL,
				DWORD dwExStyle = 0,
				CCreateContext* pContext = NULL);

// 加载框架 - load frame and associated resources
	virtual BOOL LoadFrame(UINT nIDResource,
				DWORD dwDefaultStyle = WS_OVERLAPPEDWINDOW | FWS_ADDTOTITLE,
				CWnd* pParentWnd = NULL,
				CCreateContext* pContext = NULL);

// 创建中央视图 helper for view creation
	CWnd* CreateView(CCreateContext* pContext, UINT nID = AFX_IDW_PANE_FIRST);

// 第十三章文档架构时获取激活文档
	virtual CDocument* GetActiveDocument();

//多文档架构获取激活视图 Active child view maintenance
	CView* GetActiveView() const;           // active view or NULL
	void SetActiveView(CView* pViewNew, BOOL bNotify = TRUE);
		// active view or NULL, bNotify == FALSE if focus should not be set

	// 多文档架构的让某个子框架激活，Active frame (for frames within frames -- MDI)
	virtual CFrameWnd* GetActiveFrame();

	// For customizing the default messages on the status bar
	virtual void GetMessageString(UINT nID, CString& rMessage) const;

	BOOL m_bAutoMenuEnable;
		// TRUE => menu items without handlers will be disabled

	BOOL IsTracking();

// Operations
	virtual void RecalcLayout(BOOL bNotify = TRUE); //核心排版
	virtual void ActivateFrame(int nCmdShow = -1);
	void InitialUpdateFrame(CDocument* pDoc, BOOL bMakeVisible);
	void SetTitle(LPCTSTR lpszTitle);
	CString GetTitle() const;
	
	virtual UINT GetTrackingID() { return m_nIDTracking; }

	// set/get menu bar visibility style
	virtual void SetMenuBarVisibility(DWORD dwStyle);
	virtual DWORD GetMenuBarVisibility() const;

	// set/get menu bar visibility state
	virtual BOOL SetMenuBarState(DWORD dwState);
	virtual DWORD GetMenuBarState() const;

	BOOL GetMenuBarInfo(LONG idObject, LONG idItem, PMENUBARINFO pmbi) const;

protected:
	virtual BOOL OnCreateClient(LPCREATESTRUCT lpcs, CCreateContext* pContext);

	friend class CWinApp;
};
```

**附录：CFrameWnd::LoadFrame与CreateFrame**

```
BOOL CFrameWnd::LoadFrame(UINT nIDResource, DWORD dwDefaultStyle,
	CWnd* pParentWnd, CCreateContext* pContext)
{
	CString strFullString;
	if (strFullString.LoadString(nIDResource))
		AfxExtractSubString(m_strTitle, strFullString, 0);    // first sub-string

	VERIFY(AfxDeferRegisterClass(AFX_WNDFRAMEORVIEW_REG));

	// attempt to create the window
	LPCTSTR lpszClass = GetIconWndClass(dwDefaultStyle, nIDResource);
	CString strTitle = m_strTitle;
	if (!Create(lpszClass, strTitle, dwDefaultStyle, rectDefault, 
	  pParentWnd, ATL_MAKEINTRESOURCE(nIDResource), 0L, pContext))
	{
		return FALSE;   // will self destruct on failure normally
	}

	// save the default menu handle
	ASSERT(m_hWnd != NULL);
	m_hMenuDefault = m_dwMenuBarState == AFX_MBS_VISIBLE ? ::GetMenu(m_hWnd) : m_hMenu;

	// load accelerator resource
	LoadAccelTable(ATL_MAKEINTRESOURCE(nIDResource));

	if (pContext == NULL)   // send initial update
		SendMessageToDescendants(WM_INITIALUPDATE, 0, 0, TRUE, TRUE);

	return TRUE;
}
```

### 控件类

#### CTreeCtrl

CTreeCtrl类的选中消息分析：
a)结构体：

```
typedef struct tagTVITEMCHANGE {
    NMHDR hdr;
    UINT uChanged;
    HTREEITEM hItem;
    UINT uStateNew;
    UINT uStateOld;
    LPARAM lParam;
} NMTVITEMCHANGE;
```

b)State状态分析：

```
TVIS_SELECTED（0x0002）：项被选中。
TVIS_CUT（0x0008）：项被剪切。
TVIS_DROPHILITED（0x0004）：项高亮显示，用于拖放操作。
TVIS_EXPANDED（0x0020）：项展开。
TVIS_BOLD（0x0001）：项以粗体显示。
TVIS_DISABLED（0x0040）：项禁用（灰色显示）。
TVIS_EXPANDEDONCE（0x0200）：项已经展开过一次。
TVIS_EXPANDPARTIAL（0x0400）：项部分展开。
TVIS_OVERLAYMASK（0x0F00）：覆盖层蒙版。
最后你再回头看看CListCtrl类和CTreeCtrl类，里面是啥东西？？？
```

附录1：CListView和CTreeView的原理

```// CListView
_AFXCVIEW_INLINE CListView::CListView() : CCtrlView(WC_LISTVIEW,
	AFX_WS_DEFAULT_VIEW)
	{ }
	_AFXCVIEW_INLINE CListCtrl& CListView::GetListCtrl() const
	{ return *(CListCtrl*)this; }
_AFXCVIEW_INLINE CTreeView::CTreeView() : CCtrlView(WC_TREEVIEW,
	AFX_WS_DEFAULT_VIEW)
	{ }

_AFXCVIEW_INLINE CTreeCtrl& CTreeView::GetTreeCtrl() const
	{ return *(CTreeCtrl*)this; }
```

附录2：回顾控件类的原理

其实是全都在用**SendMessage**来做事情

```
_AFXCMN_INLINE CTreeCtrl::CTreeCtrl()
	{ }
_AFXCMN_INLINE HTREEITEM CTreeCtrl::InsertItem(_In_ LPTVINSERTSTRUCT lpInsertStruct)
	{ ASSERT(::IsWindow(m_hWnd));  return (HTREEITEM)::SendMessage(m_hWnd, TVM_INSERTITEM, 0, (LPARAM)lpInsertStruct); }
_AFXCMN_INLINE HTREEITEM CTreeCtrl::InsertItem(_In_z_ LPCTSTR lpszItem, _In_ int nImage,
	_In_ int nSelectedImage, _In_ HTREEITEM hParent, _In_ HTREEITEM hInsertAfter)
	{ ASSERT(::IsWindow(m_hWnd)); return InsertItem(TVIF_TEXT | TVIF_IMAGE | TVIF_SELECTEDIMAGE, lpszItem, nImage, nSelectedImage, 0, 0, 0, hParent, hInsertAfter); }
_AFXCMN_INLINE HTREEITEM CTreeCtrl::InsertItem(_In_z_ LPCTSTR lpszItem, _In_ HTREEITEM hParent, _In_ HTREEITEM hInsertAfter)
	{ ASSERT(::IsWindow(m_hWnd)); return InsertItem(TVIF_TEXT, lpszItem, 0, 0, 0, 0, 0, hParent, hInsertAfter); }
_AFXCMN_INLINE BOOL CTreeCtrl::DeleteItem(_In_ HTREEITEM hItem)
	{ ASSERT(::IsWindow(m_hWnd)); return (BOOL)::SendMessage(m_hWnd, TVM_DELETEITEM, 0, (LPARAM)hItem); }
······
```



#### CToolBar、CContralBar

**主要属性**

```
// ControlBar styles（理论上包括状态栏、工具栏等）
#define CBRS_ALIGN_LEFT     0x1000L
#define CBRS_ALIGN_TOP      0x2000L
#define CBRS_ALIGN_RIGHT    0x4000L
#define CBRS_ALIGN_BOTTOM   0x8000L
#define CBRS_ALIGN_ANY      0xF000L//四处都可以停靠

#define CBRS_BORDER_LEFT    0x0100L
#define CBRS_BORDER_TOP     0x0200L
#define CBRS_BORDER_RIGHT   0x0400L
#define CBRS_BORDER_BOTTOM  0x0800L
#define CBRS_BORDER_ANY     0x0F00L

#define CBRS_TOOLTIPS       0x0010L 小字条提示（\n后半）
#define CBRS_FLYBY          0x0020L  状态栏提示的另一半文字
#define CBRS_FLOAT_MULTI    0x0040L
#define CBRS_BORDER_3D      0x0080L
#define CBRS_HIDE_INPLACE   0x0008L
#define CBRS_SIZE_DYNAMIC   0x0004L 可以拉扯工具栏变形
#define CBRS_SIZE_FIXED     0x0002L 固定形状（不可拉扯）
#define CBRS_FLOATING       0x0001L  

#define CBRS_GRIPPER        0x00400000L 掐子（去掉之后就是锁定工具栏的属性） 没有左边的点点，拖不动了

#define CBRS_ORIENT_HORZ    (CBRS_ALIGN_TOP|CBRS_ALIGN_BOTTOM)
#define CBRS_ORIENT_VERT    (CBRS_ALIGN_LEFT|CBRS_ALIGN_RIGHT)
#define CBRS_ORIENT_ANY     (CBRS_ORIENT_HORZ|CBRS_ORIENT_VERT)

#define CBRS_ALL            0x0040FFFFL

// the CBRS_ style is made up of an alignment style and a draw border style
//  the alignment styles are mutually exclusive
//  the draw border styles may be combined
#define CBRS_NOALIGN        0x00000000L
#define CBRS_LEFT           (CBRS_ALIGN_LEFT|CBRS_BORDER_RIGHT)
#define CBRS_TOP            (CBRS_ALIGN_TOP|CBRS_BORDER_BOTTOM)
#define CBRS_RIGHT          (CBRS_ALIGN_RIGHT|CBRS_BORDER_LEFT)
#define CBRS_BOTTOM         (CBRS_ALIGN_BOTTOM|CBRS_BORDER_TOP)
```







## MFC六大关键技术

1、MFC Initialization —— MFC程序的初始化过程

2、Message Mapping —— 消息映射

3、Message Routing —— 消息传递（路由）

4、RTTI（Runtime Type Identification）—— 运行时类型识别

5、Dynamic Creation —— 动态创建

6、Persistence ——永久保存（串行化、序列化）

### MFC程序的初始化过程

参见：CWinApp::InitInstance的虚函数，MFC内部接管WinMain平台启动初始化之后再调用InitInstance。
开发者需要创建CWinApp的派生类，并且在全局区定义派生类的全局对象，最后在派生类礼重写InitInstance虚函数。

### 消息传递（路由）

主要在框架与视图架构里，把框架收到的菜单和工具栏消息分发到各个视图类。

```
BOOL CMainFrame::OnCmdMsg(UINT nID...)
	if (m_pView && m_pView->OnCmdMsg(nID, nCode, pExtra, pHandlerInfo))
		return TRUE;
```

### RTTI  运行时类型识别

核心的作用是任何MFC的类（CObject派生）都能够获取到类型信息。
而且能知道你的派生类是谁，甚至获取到整个派生树分枝的名字。

	auto pInfo = obj.GetRuntimeClass();
	while (pInfo)
	{
	AfxMessageBox(CString(_T("你是：")) + pInfo->m_lpszClassName);
	pInfo = pInfo->m_pBaseClass;//pNext;
	}

参见：RUNTIME_CLASS宏以及每个MFC类的信息管理：

```
DECLARE_DYNAMIC(CMainFrame)
IMPLEMENT_DYNAMIC(CMainFrame, CFrameWnd)
```

RTTI运行时识别类型，靠的就是



```
BOOL CObject::IsKindOf(const CRuntimeClass* pClass) const;//用IsKindOf进行类型的识别。
CRuntimeClass* pClassThis = GetRuntimeClass();
```



#### RTTI

a)RTTI(Runtime Type Identification)是“运行时类型识别”的意思。
b)现有MFC的这项发明，后来RTTI被引入C++语言。
c)但凡是CObject派生的所有MFC类的对象都可以来探测一下他的派生来源。
d)参见CObject::IsKindOf( const CRuntimeClass* pClass  ) const;

#### RUNTIME_CLASS运行时类的原理

类中用`DECLARE_DYNAMIC(CMainFrame)`定义户籍信息

```
DECLARE_DYNAMIC(CMainFrame);//展开后的样子：（全局区的户籍信息）

static const CRuntimeClass classCMainFrame;
//定义了一个CRuntimeClass类型的镜头盖对象，每个类独一份
virtual CRuntimeClass* GetRuntimeClass() const;
//展开
```

```
#define _RUNTIME_CLASS(class_name) ((CRuntimeClass*)(&class_name::class##class_name))
//既是((CRuntimeClass*)(&CMainFrame::classCMainFrame))
```

定义户籍信息后，在cpp文件中形成一个类似树状的链表，其实就是对形成的户籍本进行赋值

用该语句进行`IMPLEMENT_DYNAMIC(class_name, base_class_name) `一般在cpp文件中执行

```
//#define IMPLEMENT_DYNAMIC(class_name, base_class_name) 
//	IMPLEMENT_RUNTIMECLASS(CMainFrame, CFrameWnd, 0xFFFF, NULL, NULL)

//展开即：

AFX_COMDAT const CRuntimeClass CMainFrame::classCMainFrame = { 
"CMainFrame", sizeof(class CMainFrame), 0xFFFF, NULL, 
	RUNTIME_CLASS(CFrameWnd), NULL, NULL }; 
CRuntimeClass* CMainFrame::GetRuntimeClass() const
{ 
	return RUNTIME_CLASS(CMainFrame); 
}
//可以理解为对结构体成员进行赋值。其中	RUNTIME_CLASS(CFrameWnd)就是对CRuntimeClass::m_pBaseClass赋值，形成链表。
```

CRuntimeClass类：

```
struct CRuntimeClass
{
// Attributes
	LPCSTR m_lpszClassName;
	int m_nObjectSize;
	UINT m_wSchema; // schema number of the loaded class
	CObject* (PASCAL* m_pfnCreateObject)(); // NULL => abstract class
#ifdef _AFXDLL
	CRuntimeClass* (PASCAL* m_pfnGetBaseClass)();
#else
	CRuntimeClass* m_pBaseClass; //
#endif

// Operations
	CObject* CreateObject();
	BOOL IsDerivedFrom(const CRuntimeClass* pBaseClass) const;
。。。
```

IsKindOf()内部有一个循环，可以循环追踪。



## Tips

### 待定

#### 获取Bitmap的宽高 

```
CSize CBitmap::GetBitmapDimension();//获取位图的Size,但是在恢复Rgn的时候使用会不好使。
CSize ss = dc.GetCurrentBitmap()->GetBitmapDimension();//获得的值竟然是空的。
```

#### 图片加载.bmp .ico .cur

都可以用LoadImage加载

例如Bitmap

```c++
HBITMAP hBitmap = (HBITMAP)LoadImage(NULL,sFile, IMAGE_BITMAP, 0, 0, LR_LOADFROMFILE);、
```

#### 四大HDC句柄

1. 标准绘图句柄：BeginPaint和EndPaint
2. 临时客户区句柄：GetDC和ReleaseDC
3. 非客户区绘图句柄：GetWindowDC和ReleaseDC
4. 内存绘图句柄：CreateCompatibleDC 和 DeleteDC

#### 图片不能加载

- 路径问题，在Debug中双击exe运行时，相对路径以exe为基准，因此检索不到res文件夹，不能显示图片，应放在同一目录。

#### SetWindowRgn失效期

SetWindowRgn(CRgn rgn, TRUE); rgn 在使用后会被废掉，若使用已保存好的Rgn数组，则应当rgn.CopyRgn出来后再使用。

#### VC6.0 pch.h

VC6.0中 pch.h文件时StdAfx.h

#### 填充背景色函数

```
pDC->FillSolidRect(rect, GetSysColor(COLOR_INFOBK));
```

#### 调用系统GDI的函数

```
LoadStandardCursor();
LoadStandardIcon();
GetStockObject();
//等。
```

#### CChildView

框架视图中这个类往往没啥用，可以干掉。

#### CListView初始化时不显示字段与窗格

```
list.ModifyStyle(0, LVS_REPORT);//加上这条语句就好了
```

个人感觉是View视图控件和默认预设的控件没有什么本质区别。

在使用对话框创建控件时还需要进行预设属性，对属性不够明晰了解是可以考虑使用对话框对属性进行探究。

这里LVS_REPORT是在对话框资源窗口就修改完成了，在View中还需要进行一下自己的设置。

#### 随笔记录

1. CS架构的客户端不需要链接数据库，因为数据是通过网络协议发送和接收的。

#### 按住alt加鼠标左键可以实现方框拖选。

#### 构造函数时搞App对象

#### 屏幕绘制、QQ截图

他们都不是真实的截图，而是搞出了一个全屏的截图窗口，进行截取与绘制。

#### 实际开发中，用重写OnDraw虚函数进行绘制

因为重写OnPaint基类的东西就不能用了。

#### 消息映射精简

例如绘图项目中，用到了7个消息映射，每个映射仅有一行代码，此时可以用这个宏进行精简。

研究区间命令管理，把7套命令和状态管理函数合并成1套。

范围精简：

```
#define ON_COMMAND_RANGE(id, idLast, memberFxn) 
#define ON_UPDATE_COMMAND_UI_RANGE(id, idLast, memberFxn) 
```

```\
BEGIN_MESSAGE_MAP(CMainView, CView)
	ON_COMMAND_RANGE(ID_DRAW_DRAG, ID_DRAW_RRECT, OnDrawCommad)
	ON_UPDATE_COMMAND_UI_RANGE(ID_DRAW_DRAG, ID_DRAW_RRECT, OnUpdateDrawUI)
END_MESSAGE_MAP()

void CMainView::OnDrawCommad(UINT nID)
{//7个函数合成一个，非常的方便
	m_nIndex = nID;
}
void CMainView::OnUpdateDrawUI(CCmdUI* pCmdUI)
{
	pCmdUI->SetCheck(m_nIndex == pCmdUI->m_nID);
}
```











## 项目记录  

### CBitmapButton三态按钮开发

#### 鼠标离开控件切换Bitmap

鼠标在离开控件的瞬间，WM_MOUSEMOVE消息会失效，所以这里不能通过PtInRect判断。

此处有两种方法：

1. 利用WM_MOUSELEAVE消息：需要TrackMouseEvent来追踪。

2. SetCapture和ReleaseCapture：设置捕捉。

WM_MOUSELEAVE消息：

```
void CButtonYXX::OnMouseMove(UINT nFlags, CPoint point)
{//在代码中调用TrackMouseEvent(&tme);这样在离开时就会发送一条WM_MOUSELEAVE消息。
	if (!m_track)
	{
		TRACKMOUSEEVENT tme;
		tme.cbSize = sizeof(TRACKMOUSEEVENT);
		tme.dwFlags = TME_LEAVE;
		tme.hwndTrack = m_hWnd;
		TrackMouseEvent(&tme);
		
		m_track = TRUE;
		Invalidate(FALSE);
	}
	CWnd::OnMouseMove(nFlags, point);
}
void CButtonYXX::OnMouseLeave()
{
	m_track = FALSE;
	Invalidate(FALSE);
	CWnd::OnMouseLeave();
}
```

 SetCapture

```
void CButtonYXX::OnMouseMove(UINT nFlags, CPoint point)
{//进入onmousemove函数即是在控件中，若m_track==0，说明是从外进来，则SetCapture。
	CRect rect;
	GetClientRect(&rect);
	if (!m_track)
	{
		SetCapture();
		m_track = TRUE;
		Invalidate(FALSE);
	}
	if (!rect.PtInRect(point))
	{//若离开，此时因为SetCapture函数，在函数中，但是点不在矩形中，所以用PtInRect判断
	//若不在矩形内，又在MOUSEMOVE函数内，是从控件中离开，所以ReleaseCapture()。
		ReleaseCapture();
		m_track = FALSE;
		Invalidate(FALSE);
	}
	CWnd::OnMouseMove(nFlags, point);
}
```

#### bitmap三态切换代码示意

个人感觉要点就是，选择nID来决定贴图，用m_track、m_select、和m_Outdown来选择显示什么图


```
void CButtonYXX::OnPaint()//作为主绘图，用m_track和nID作为判断，最后选择到底显示绘制什么图片。
{
	CPaintDC dc(this); // device context for painting
	CRect rect;
	GetClientRect(rect);
//用GetClient代替获取BITMAP结构体信息以降低开支。
	int nID = BT_NORMAL;
	if(m_track)
		nID = BT_FOCUS;
	if(m_select)
		nID = BT_SELECT;
	if(m_Outdown)
		nID = BT_FOCUS;
	//这里的判断优先级有强弱之分的。
	dc.BitBlt(0, 0, rect.Width(), rect.Height(), &m_dc[nID], 0, 0, SRCCOPY);
}
```


```
void CButtonYXX::OnMouseMove(UINT nFlags, CPoint point)
{//核心算法
	static BOOL ifSelRefresh = FALSE;//设置状态
	CRect rect;
	GetClientRect(&rect);
	if (ifSelRefresh == TRUE)
	{//利用静态变量判断，使得从页面外回来并松开点击时可以刷新一次。
		m_Outdown = FALSE;
		Invalidate(FALSE);
	}
	if (!m_track)
	{//进入空间时，赋值m_track并刷新一次。
		SetCapture();
		m_track = TRUE;
		if(!m_select)//有m_select就不刷新这个了，防止冲突，这个没啥用
			Invalidate(FALSE);
	}
	if (!rect.PtInRect(point))
	{//从矩形内移到控件外触发，
		if (nFlags == MK_LBUTTON )
		{//按住左键离开
			if (!m_Outdown)
			{//使m_Outdown为TRUE，并刷新一次。
				m_Outdown = TRUE;
				ifSelRefresh = TRUE;
				Invalidate(FALSE);
			}
		}
		else
		{//离开举行外并没按住左键，一切归0
			m_select = FALSE;
			m_track = FALSE;
			m_Outdown = FALSE;
			ReleaseCapture();
			Invalidate(FALSE);
		}	
	}	
	CWnd::OnMouseMove(nFlags, point);
}
void CButtonYXX::OnMouseLeave()
{
	//m_track = FALSE;
	//Invalidate(FALSE);
	CWnd::OnMouseLeave();
}
void CButtonYXX::OnLButtonDown(UINT nFlags, CPoint point)
{
//单击强制触发刷新一次。
	m_select = TRUE;
	Invalidate(FALSE);
	CWnd::OnLButtonDown(nFlags, point);
}
void CButtonYXX::OnLButtonUp(UINT nFlags, CPoint point)
{松开则一切归0,
	CRect rect;
	GetClientRect(&rect);
	ReleaseCapture();
	if (rect.PtInRect(point))
	{
		//执行代码
		AfxMessageBox(_T("hh"));
	}
	m_select = FALSE;
	m_track = FALSE;
	m_Outdown = FALSE;
	Invalidate(FALSE);
	CWnd::OnLButtonUp(nFlags, point);
}
```

### 封装CMemoryDC类

利用CMemoryDC类，可以在CDC的基础上添加功能。

如 挖去背景、加载位图到CDC

#### CMemoryDC类

```
#include <afxwin.h>
class CMemoryDC :public CDC
{
public:
	CMemoryDC():m_size{}
	{
		
	}
	CMemoryDC(UINT nIDResource)
	{
		LoadBitmap(nIDResource);
	}
	~CMemoryDC()
	{

	}
	void MakeRgn(CRgn& rResource, COLORREF col)
	{
		if(!rResource.GetSafeHandle())
			rResource.CreateRectRgn(0, 0, 0, 0);
		for (int i = 0; i < m_size.cy; ++i)
		{
			for (int j = 0; j < m_size.cx; ++j)
			{
				if (GetPixel(j, i) != col)
				{
					CRgn rTemp;
					rTemp.CreateRectRgn(j, i, j + 1, i + 1);//1x1 像素,这里的ij有一点颠倒
					rResource.CombineRgn(&rResource, &rTemp, RGN_OR);
				}
			}
		}
	}

	BOOL LoadBitmap(UINT nIDResource,CDC* pDC = NULL)//后面这个参数不知道干嘛的
	{
		if (!CreateCompatibleDC(NULL))
			return FALSE;//创建DC，这个比较快，先判断
		CBitmap bmp;
		if (!bmp.LoadBitmap(nIDResource))
		{
			DeleteDC();//防止之前创建了DC但是没成功加载图片
			return FALSE;//LoadBitmap比较慢，后判断
		}
		BITMAP bm;
		bmp.GetBitmap(&bm);
		SelectObject(&bmp);
		m_size.SetSize(bm.bmWidth, bm.bmHeight);
		return TRUE;
	}
	CSize GetSize()const
	{
		return m_size;
	}
	int GetWidth()const
	{
		return m_size.cx;
	}
	int GetHeight()const
	{
		return m_size.cy;
	}
protected:
	CSize m_size;
//	CDC m_dc;//不用这个，因为基类就有
};
```

### Rgn动图

类中成员。

```
protected:
	CPoint m_pos;
	int m_x, m_y;
	enum {STM_FLYMOVE=8888};
	CMemoryDC m_dcBack;
	CMemoryDC m_dcFlys[7];
	CRgn m_rFlys[7];//加载的时候放到数组中就可以节省切换时候的内存开销，是一个很好的方法。
	int m_nFlyIndex;//切换动画
// 构造
```

### CView实现CS架构管理系统

利用CListView做主视图

- 新建项目
- 产出CChileView相关
- 自CListView派生CMainView类
- pch.h包含CListView的头文件afxcview.h
- 在CMainFrame::OnCreate中创建视图

```c++
CCreateContext cc;//创建视图
cc.m_pNewViewClass = RUNTIME_CLASS(CMainView));
CreateView(&cc);
```

- 虚函数`OnInitialUpdate()`中

```c++
CListCtrl& list = GetListCtrl();
//list.ModifyStyle(0, LVS_REPORT);
list.InsertColumn(0, _T("工号"), 0, 180);
list.InsertColumn(1, _T("姓名"), 0, 180);
list.InsertColumn(2, _T("工资"), 0, 180);
list.InsertColumn(3, _T("入职日期"), 0, 180);
list.SetExtendedStyle(LVS_EX_FULLROWSELECT | LVS_EX_GRIDLINES);
```



### DrawYxx 绘图项目

利用多文档视图架构实现。

- 制造右侧停靠的窗口，编辑绘图的界面，绘制与修改ToolBar，并设置调配ToolBar属性。

- 创建工具栏属性的映射函数
- 制作点击切换工具栏选中显示。



#### CContralBar切换、ToolBar单击切换选中

做法是和UI有关系，一个ToolBarID，在类视图中可以建立两个映射函数，一个是COMMAND，一个是下面的ui函数。

用

```
	//CMainView类中，用m_nIndex作为记录，类似于蝴蝶的切换。
	int m_nIndex{ ID_DRAW_DRAG };//初始化ID为第一个，一共有七个。
```



```
void CMainView::OnDrawDrag()
{//COMMAND 用于给m_nIndex赋值和判断
	m_nIndex = ID_DRAW_DRAG;
}
void CMainView::OnDrawEllipse()
{
	m_nIndex = ID_DRAW_ELLIPSE;
}
```

```
void CMainView::OnUpdateDrawDrag(CCmdUI* pCmdUI)
{//利用UI进行修改，m_nIndex == pCmdUI->m_nID用于改变FALSE还是TRUE。
	pCmdUI->SetCheck(m_nIndex == pCmdUI->m_nID);
}
void CMainView::OnUpdateDrawEllipse(CCmdUI* pCmdUI)
{
	pCmdUI->SetCheck(m_nIndex == pCmdUI->m_nID);
}
```

#### SLayer纯虚架构

SLayer 作为基类，CLine、CPencil等类都由此派生，记录和调用都归派生类

```
struct SLayer
{//做成纯虚函数，貌似纯虚了就不用写定义了。
	virtual void OnMouseMove(UINT nFlags, CPoint point) = 0;
	virtual void OnLButtonUp(UINT nFlags, CPoint point) = 0;
	virtual void OnLButtonDown(UINT nFlags, CPoint point) = 0;
	virtual void OnDraw(CDC* pDC) = 0;
};
```

例如CLine

```
class CLine : public SLayer
{//核心就是两个点
	CPoint m_ps, m_pe;//Start  End;
	virtual void OnMouseMove(UINT nFlags, CPoint point);
	virtual void OnLButtonUp(UINT nFlags, CPoint point);//记录m_pe
	virtual void OnLButtonDown(UINT nFlags, CPoint point);//记录m_ps
	virtual void OnDraw(CDC* pDC);//用MoveTo   LineTo绘制
};
```

在CMainView中：

```
void CMainView::OnLButtonDown(UINT nFlags, CPoint point)
{
	SLayer* pLayer = nullptr;
	switch (m_nIndex)
	{
	case ID_DRAW_LINE:
		pLayer = new CLine;
		break;
	case ID_DRAW_PENCIL:
		pLayer = new CLine;
		break;
	}
	if (pLayer != nullptr)
	{//虚函数架构在这里就十分的方便了。
		pLayer->OnLButtonDown(nFlags,point);
		m_ls.Add(pLayer);
	}
	CView::OnLButtonDown(nFlags, point);
}
void CMainView::OnLButtonUp(UINT nFlags, CPoint point)
{
	int nCount = m_ls.GetCount();
	if (nCount < 1)
		return;
	m_ls[--nCount]->OnLButtonUp(nFlags, point);//调用各自类对象的函数记录核心数据
	Invalidate();
	CView::OnLButtonUp(nFlags, point);
}
void CMainView::OnDraw(CDC* pDC)
{
	int nCount = m_ls.GetCount();
	for (int i = 0; i < nCount; ++i)
	{
		m_ls[i]->OnDraw(pDC);//调用各自的类进行绘制，十分节省代码量
	}
}
```









#### 
