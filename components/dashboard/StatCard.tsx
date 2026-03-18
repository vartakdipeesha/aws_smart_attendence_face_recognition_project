import React from 'react';
import { Card } from '../ui/Card';

interface StatCardProps {
    title: string;
    value: string | number;
    icon: React.ReactNode;
}

export const StatCard: React.FC<StatCardProps> = ({ title, value, icon }) => {
    return (
        <Card className="flex items-center p-4">
            <div className="p-3 mr-4 text-brand-accent bg-brand-accent/20 rounded-full">
                {icon}
            </div>
            <div>
                <p className="text-sm font-medium text-gray-400">{title}</p>
                <p className="text-2xl font-bold text-white">{value}</p>
            </div>
        </Card>
    );
};