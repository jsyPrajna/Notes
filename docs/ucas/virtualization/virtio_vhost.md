# Virtio/Vhost

[virtio 简介 - 猿大白 - 博客园 (cnblogs.com)](https://www.cnblogs.com/bakari/p/8309638.html)

[Virtio Devices High-Level Design — Project ACRN™ 2.7-unstable documentation](https://projectacrn.github.io/latest/developer-guides/hld/hld-virtio-devices.html)

[Stefan Hajnoczi: QEMU Internals: vhost architecture (vmsplice.net)](http://blog.vmsplice.net/2011/09/qemu-internals-vhost-architecture.html)

[Virtio Spec Overview · kernelgo](https://kernelgo.org/virtio-overview.html)

[Modern Virtualization - Yizhou Shan's Home Page (lastweek.io)](http://lastweek.io/notes/virt/)

Virio 要点：

- 半虚拟化，共享内存

- virtqueue 传输数据

- virtqueue 组成：

  - Descriptor Table：存放IO传输请求信息；
  - Available Ring：记录了Descriptor Table表中的I/O请求下发信息，前端Driver可写后端只读；
  - Used Ring：记录Descriptor Table表中已被提交到硬件的信息，前端Driver只读后端可写。

  ```
  +-------------------+--------------------------------+-----------------------+
  | Descriptor Table  |   Available Ring  (padding)    |       Used Ring       |
  +-------------------+--------------------------------+-----------------------+
  ```

- virtqueue 数据传输流程:

  - 前端驱动将 I/O 请求放到 `Descriptor Table` 中，然后将索引更新到 `Available Ring` 中，最后 kick 后端去取数据；
  - 后端取出 I/O 请求进行处理，然后将结果刷新到 `Descriptor Table` 中再更新 `Using Ring` ，然后发送中断 notify 前端。

  ```
                            +------------------------------------+
                            |       virtio  guest driver         |
                            +-----------------+------------------+
                              /               |              ^
                             /                |               \
                            put            update             get
                           /                  |                 \
                          V                   V                  \
                     +----------+      +------------+        +----------+
                     |          |      |            |        |          |
                     +----------+      +------------+        +----------+
                     | available|      | descriptor |        |   used   |
                     |   ring   |      |   table    |        |   ring   |
                     +----------+      +------------+        +----------+
                     |          |      |            |        |          |
                     +----------+      +------------+        +----------+
                     |          |      |            |        |          |
                     +----------+      +------------+        +----------+
                          \                   ^                   ^
                           \                  |                  /
                           get             update              put
                             \                |                /
                              V               |               /
                             +----------------+-------------------+
                             |       virtio host backend          |
                             +------------------------------------+
  ```

- virtio 前后端通信机制：

  - 前端驱动访问 QEMU 设置的 MMIO 空间会触发 VM Exit，陷入到 KVM 后通过 `ioeventfd` 通知 QEMU；
  - 后端通过 `irqfd` 中断的方式通知前端。

  ```
               +-------------+                +-------------+
               |             |                |             |
               |             |                |             |
               |   GuestOS   |                |     QEMU    |
               |             |                |             |
               |             |                |             |
               +---+---------+                +----+--------+
                   |     ^                         |    ^
                   |     |                         |    |
               +---|-----|-------------------------|----|---+
               |   |     |                irqfd    |    |   |
               |   |     +-------------------------+    |   |
               |   |  ioeventfd                         |   |
               |   +------------------------------------+   |
               |                   KVM                      |
               +--------------------------------------------+
  ```

- vhost 方案：将 virtio 后端的数据传输部分放到 host 内核中，减少使用数据传输时的特权级切换。而控制相关部分，如 virtio 协商、实施迁移等还在 QEMU 中。
