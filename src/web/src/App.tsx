import React from 'react';
import { Form, Input, Select, Button, message, DatePicker } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Option } = Select;

interface EmployeeForm {
  name: string;
  domain_account: string;
  gender: string;
  hometown: string;
  university: string;
  major: string;
  phone: string;
  id_card: string;
  position: string;
  join_date: string;
}

const App: React.FC = () => {
  const [form] = Form.useForm<EmployeeForm>();

  const onFinish = async (values: EmployeeForm) => {
    try {
      // 格式化日期，确保只包含年月日
      const formattedValues = {
        ...values,
        join_date: values.join_date.format('YYYY-MM-DD')
      };
      await axios.post(`http://${window.location.hostname}:8000/api/employees`, formattedValues);
      message.success('信息提交成功！');
      form.resetFields();
    } catch (error) {
      const errorDetail = error.response?.data?.detail || error.message;
      message.error(
        <div>
          <p>提交失败，错误信息：</p>
          <pre style={{ whiteSpace: 'pre-wrap', maxHeight: '200px', overflow: 'auto' }}>
            {typeof errorDetail === 'object' ? JSON.stringify(errorDetail, null, 2) : errorDetail}
          </pre>
        </div>
      );
      console.error('提交失败:', errorDetail);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: '40px auto', padding: '0 20px' }}>
      <h1 style={{ textAlign: 'center', marginBottom: 40 }}>员工信息填写</h1>
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        autoComplete="off"
      >
        <Form.Item
          name="name"
          label="姓名"
          rules={[{ required: true, message: '请输入姓名' }]}
        >
          <Input prefix={<UserOutlined />} placeholder="请输入您的姓名" />
        </Form.Item>

        <Form.Item
          name="domain_account"
          label="域账号"
          rules={[{ required: true, message: '请输入域账号' }]}
        >
          <Input placeholder="请输入您的域账号" />
        </Form.Item>

        <Form.Item
          name="gender"
          label="性别"
          rules={[{ required: true, message: '请选择性别' }]}
        >
          <Select placeholder="请选择性别">
            <Option value="男">男</Option>
            <Option value="女">女</Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="hometown"
          label="家乡"
          rules={[{ required: true, message: '请输入家乡' }]}
        >
          <Input placeholder="请输入您的家乡" />
        </Form.Item>

        <Form.Item
          name="university"
          label="毕业院校"
          rules={[{ required: true, message: '请输入毕业院校' }]}
        >
          <Input placeholder="请输入您的毕业院校" />
        </Form.Item>

        <Form.Item
          name="major"
          label="专业"
          rules={[{ required: true, message: '请输入专业' }]}
        >
          <Input placeholder="请输入您的专业" />
        </Form.Item>

        <Form.Item
          name="phone"
          label="联系电话"
          rules={[{ required: true, message: '请输入联系电话' },
                 { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码' }]}
        >
          <Input placeholder="请输入您的联系电话" />
        </Form.Item>

        <Form.Item
          name="id_card"
          label="身份证号"
          rules={[{ required: true, message: '请输入身份证号' },
                 { pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/, message: '请输入正确的身份证号' }]}
        >
          <Input placeholder="请输入您的身份证号" />
        </Form.Item>

        <Form.Item
          name="position"
          label="职级"
          rules={[{ required: true, message: '请选择职级' }]}
        >
          <Select placeholder="请选择职级">
            <Option value="P2-1">P2-1</Option>
            <Option value="P2-2">P2-2</Option>
            <Option value="P2-3">P2-3</Option>
            <Option value="P3-1">P3-1</Option>
            <Option value="P3-2">P3-2</Option>
            <Option value="P3-3">P3-3</Option>
            <Option value="P4-1">P4-1</Option>
            <Option value="P4-2">P4-2</Option>
            <Option value="P4-3">P4-3</Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="join_date"
          label="入职日期"
          rules={[{ required: true, message: '请选择入职日期' }]}
        >
          <DatePicker
            style={{ width: '100%' }}
            placeholder="请选择入职日期"
            format="YYYY-MM-DD"
          />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" block size="large">
            提交信息
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default App;