#!/usr/bin/env python3
"""
问卷星自动填写脚本 - 简单版本
适用于：https://v.wjx.cn/vm/w7MiF02.aspx#
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import random


class QuestionnaireFiller:
    """问卷填写器"""

    def __init__(self, url: str):
        self.url = url
        self.driver = None

    def setup_driver(self):
        """设置浏览器"""
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            print("✓ 浏览器启动成功")
        except Exception as e:
            print(f"✗ 浏览器启动失败：{e}")
            raise

    def fill_random(self):
        """随机填写问卷"""
        try:
            self.driver.get(self.url)
            time.sleep(2)

            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.field"))
            )
            print("✓ 页面加载成功")

            # 获取所有题目
            questions = self.driver.find_elements(By.CSS_SELECTOR, "div.field")
            print(f"✓ 检测到 {len(questions)} 道题目")

            # 逐题填写
            for i, q in enumerate(questions, 1):
                try:
                    self._fill_question(q, i)
                    time.sleep(random.uniform(0.3, 0.8))
                except Exception as e:
                    print(f"⚠ 第{i}题填写失败：{e}")

            # 提交
            self._submit()
            return True

        except Exception as e:
            print(f"✗ 填写失败：{e}")
            return False

    def _fill_question(self, element, num: int):
        """填写单道题目"""
        # 单选题
        radios = element.find_elements(By.CSS_SELECTOR, "input[type='radio']")
        if radios:
            visible = [r for r in radios if r.is_displayed()]
            if visible:
                random.choice(visible).click()
                print(f"✓ 第{num}题（单选）已填写")
            return

        # 多选题
        checkboxes = element.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        if checkboxes:
            visible = [c for c in checkboxes if c.is_displayed()]
            if visible:
                # 随机选择 2-3 个
                num_select = random.randint(2, min(3, len(visible)))
                chosen = random.sample(visible, num_select)
                for cb in chosen:
                    try:
                        cb.click()
                    except:
                        pass
                print(f"✓ 第{num}题（多选）已填写")
            return

        # 填空题
        inputs = element.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
        if inputs:
            answers = ["非常好", "比较满意", "还可以", "支持发展", "值得推广"]
            inputs[0].send_keys(random.choice(answers))
            print(f"✓ 第{num}题（填空）已填写")
            return

        # 下拉题
        selects = element.find_elements(By.CSS_SELECTOR, "select")
        if selects:
            for s in selects:
                try:
                    sel = Select(s)
                    if len(sel.options) > 1:
                        sel.select_by_index(random.randint(1, len(sel.options) - 1))
                except:
                    pass
            print(f"✓ 第{num}题（下拉）已填写")

    def _submit(self):
        """提交问卷"""
        try:
            submit_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input#submit_button, button#submit_button, #ctlNext"))
            )
            submit_btn.click()
            print("✓ 已提交问卷")

            # 等待提交成功
            time.sleep(3)
            if "success" in self.driver.current_url.lower() or "complete" in self.driver.current_url.lower():
                print("✓ 提交成功")
        except Exception as e:
            print(f"⚠ 提交可能失败：{e}")

    def run(self, times: int = 100, interval: int = 5):
        """运行批量填写"""
        print(f"\n开始任务：填写{times}次")
        print("=" * 60)

        success_count = 0
        fail_count = 0

        for i in range(times):
            print(f"\n【第 {i+1}/{times} 次】")
            
            try:
                if self.fill_random():
                    success_count += 1
                    print(f"✅ 成功 ({success_count}/{fail_count})")
                else:
                    fail_count += 1
                    print(f"❌ 失败 ({success_count}/{fail_count})")
            except Exception as e:
                fail_count += 1
                print(f"❌ 异常：{e}")

            # 间隔等待
            if i < times - 1:
                wait_time = interval + random.uniform(0, 2)
                print(f"⏳ 等待 {wait_time:.1f} 秒...")
                time.sleep(wait_time)

        print("\n" + "=" * 60)
        print(f"任务完成！成功：{success_count}, 失败：{fail_count}")

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("✓ 浏览器已关闭")


def main():
    """主函数"""
    url = "https://v.wjx.cn/vm/w7MiF02.aspx#"
    
    print("=" * 60)
    print("问卷星自动填写工具")
    print("问卷：AI 驱动智能招聘与人才画像影响因素调查")
    print("=" * 60)

    filler = QuestionnaireFiller(url)
    
    try:
        filler.setup_driver()
        filler.run(times=100, interval=5)
    except KeyboardInterrupt:
        print("\n⚠ 用户中断")
    except Exception as e:
        print(f"\n✗ 错误：{e}")
    finally:
        filler.close()


if __name__ == "__main__":
    main()
