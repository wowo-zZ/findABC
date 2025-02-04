import React from 'react';
import { Form, Input, Select, Button, message } from 'antd';
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
  department?: string;
  position: string;
}

const App: React.FC = () => {
  const [form] = Form.useForm<EmployeeForm>();

  const onFinish = async (values: EmployeeForm) => {
    try {
      await axios.post('http://localhost:8000/api/employees', values);
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
          rules={[{ required: true, message: '请输入联系电话' }]}
        >
          <Input placeholder="请输入您的联系电话" />
        </Form.Item>

        <Form.Item
          name="department"
          label="所属部门"
        >
          <Input placeholder="请输入您的所属部门（选填）" />
        </Form.Item>

        <Form.Item
          name="position"
          label="职位"
          rules={[{ required: true, message: '请输入职位' }]}
        >
          <Input placeholder="请输入您的职位" />
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